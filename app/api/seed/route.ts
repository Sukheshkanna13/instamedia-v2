import { NextRequest, NextResponse } from "next/server";
import { createServerSupabase } from "@/lib/supabase";
import { embedText } from "@/lib/embeddings";
import { calculateERS } from "@/lib/utils";
import fs from "fs";
import path from "path";

// A robust CSV line parser that handles quoted strings containing commas
function parseCSVLine(line: string): string[] {
    const result = [];
    let cur = "";
    let inQuote = false;
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"' && (i === 0 || line[i - 1] !== '\\')) {
            inQuote = !inQuote;
        } else if (char === ',' && !inQuote) {
            result.push(cur.replace(/^"|"$/g, ''));
            cur = "";
        } else {
            cur += char;
        }
    }
    result.push(cur.replace(/^"|"$/g, ''));
    return result;
}

export async function POST(req: NextRequest) {
    const supabase = createServerSupabase();

    if (!supabase) {
        return NextResponse.json(
            { error: "Supabase not configured locally" },
            { status: 503 }
        );
    }

    const csvPath = path.join(process.cwd(), "data", "brand_posts.csv");
    if (!fs.existsSync(csvPath)) {
        return NextResponse.json(
            { error: `CSV not found at ${csvPath}` },
            { status: 404 }
        );
    }

    try {
        const fileContent = fs.readFileSync(csvPath, "utf-8");
        const lines = fileContent.split(/\r?\n/).filter(line => line.trim() !== "");

        console.log(`[SEED] Reading ${csvPath}`);
        console.log(`[SEED] File length: ${fileContent.length}, lines: ${lines.length}`);

        let added = 0;
        let skipped = 0;
        const insertErrors: any[] = [];

        // Skip header line (index 0)
        for (let i = 1; i < lines.length; i++) {
            const row = parseCSVLine(lines[i]);
            if (row.length < 5) continue;

            const post_text = row[0].trim();
            const likes = parseInt(row[1]) || 0;
            const comments = parseInt(row[2]) || 0;
            const shares = parseInt(row[3]) || 0;
            const platform = (row[4] || "instagram").trim().toLowerCase();

            const ers = calculateERS(likes, comments, shares);

            // Check if already exists (using exact match on content)
            const { data: existing, error: existingError } = await supabase
                .from("posts_embeddings")
                .select("id")
                .eq("document", post_text)
                .limit(1);

            if (existingError) {
                insertErrors.push({ type: "select", error: existingError });
                continue;
            }

            if (existing && existing.length > 0) {
                skipped++;
                continue;
            }

            try {
                // Generate embedding
                const embedding = await embedText(post_text);

                if (!embedding || embedding.length !== 768) {
                    insertErrors.push({ type: "embedding_failure", text: post_text.slice(0, 50), len: embedding?.length || 'undefined' });
                    continue;
                }

                // Insert into Supabase
                const { error: insertError } = await supabase
                    .from("posts_embeddings")
                    .insert({
                        document: post_text,
                        content: post_text,
                        embedding,     // pgvector column
                        ers,
                        likes,
                        comments,
                        shares,
                        platform,
                        metadata: { source: "seed" }
                    });

                if (insertError) {
                    insertErrors.push({ type: "insert", error: insertError });
                } else {
                    added++;
                }
            } catch (err: any) {
                insertErrors.push({ type: "embedText", error: err.message || err });
            }
        }

        const { count } = await supabase
            .from("posts_embeddings")
            .select('*', { count: 'exact', head: true });

        return NextResponse.json({
            success: true,
            added,
            skipped,
            total: count ?? 0,
            debug: {
                cwd: process.cwd(),
                csv_path: csvPath,
                file_length: fileContent.length,
                lines_length: lines.length,
                errors: insertErrors.slice(0, 5),
            }
        });

    } catch (e: any) {
        return NextResponse.json(
            { error: e.message || "Failed to seed database" },
            { status: 500 }
        );
    }
}
