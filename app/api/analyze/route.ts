import { NextRequest, NextResponse } from "next/server";
import { runAnalyze } from "@/lib/agents/analyze-graph";

export async function POST(req: NextRequest) {
    try {
        const data = await req.json();
        const draft = (data.draft ?? "").trim();
        const brandId = data.brand_id ?? "default";

        if (!draft || draft.length < 10) {
            return NextResponse.json(
                { error: "Draft too short" },
                { status: 400 }
            );
        }

        const result = await runAnalyze(draft, brandId);

        if (result.error) {
            return NextResponse.json(
                { success: false, error: result.error },
                { status: 500 }
            );
        }

        return NextResponse.json({
            success: true,
            draft,
            analysis: result.analysis,
            reference_posts: result.topPosts.slice(0, 3).map((p) => ({
                text: p.text,
                ers: p.ers,
                semantic_sim: p.similarity,
                platform: p.platform,
            })),
            processing_time_seconds: result.processingTime,
            db_size: result.dbSize,
            banned_words_found: result.foundBanned,
        });
    } catch (e) {
        return NextResponse.json(
            { success: false, error: (e as Error).message },
            { status: 500 }
        );
    }
}
