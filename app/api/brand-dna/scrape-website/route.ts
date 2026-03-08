import { NextRequest, NextResponse } from "next/server";
import { createServerSupabase } from "@/lib/supabase";
import { embedText } from "@/lib/embeddings";

export async function POST(req: NextRequest) {
    const supabase = createServerSupabase();
    if (!supabase) {
        return NextResponse.json({ error: "Supabase not configured locally" }, { status: 503 });
    }

    try {
        const data = await req.json();
        const url = data.url?.trim();
        const brandId = data.brand_id ?? "default";

        if (!url) {
            return NextResponse.json({ error: "URL is required" }, { status: 400 });
        }

        const res = await fetch(url, { headers: { "User-Agent": "InstaMedia-Bot/1.0" } });
        if (!res.ok) {
            throw new Error(`Failed to fetch URL: ${res.statusText}`);
        }

        const html = await res.text();

        // Strip scripts and styles safely
        let cleanText = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, " ");
        cleanText = cleanText.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, " ");

        // Strip general HTML tags
        cleanText = cleanText.replace(/<[^>]+>/g, " ");

        // Clean excess whitespace
        cleanText = cleanText.replace(/\s+/g, " ").trim();

        if (cleanText.length < 50) {
            throw new Error("Could not extract meaningful text from website");
        }

        // Chunking (naive 1000 chars per chunk)
        const CHUNK_SIZE = 1000;
        const chunks = [];
        for (let i = 0; i < cleanText.length; i += CHUNK_SIZE) {
            chunks.push(cleanText.slice(i, i + CHUNK_SIZE));
        }

        // Keep up to 20 chunks to avoid massive loops, filter tiny chunks
        const validChunks = chunks.slice(0, 20).filter(c => c.length > 50);

        // Clear existing website context for this brand
        await supabase
            .from("posts_embeddings")
            .delete()
            .eq("platform", "website")
            .eq("metadata->>brand_id", brandId);

        let embeddedCount = 0;
        for (const chunk of validChunks) {
            try {
                const embedding = await embedText(chunk);
                await supabase.from("posts_embeddings").insert({
                    document: chunk,
                    content: chunk,
                    embedding,
                    ers: 0,
                    likes: 0,
                    comments: 0,
                    shares: 0,
                    platform: "website",
                    metadata: { source: "website", brand_id: brandId }
                });
                embeddedCount++;
            } catch (err) {
                console.error("Chunk embed failed", err);
            }
        }

        return NextResponse.json({
            success: true,
            data: {
                brand_id: brandId,
                chunks_processed: embeddedCount,
                message: "Website context added to AI knowledge base."
            }
        });

    } catch (e: any) {
        return NextResponse.json(
            { success: false, error: e.message || "Failed to scrape website" },
            { status: 500 }
        );
    }
}
