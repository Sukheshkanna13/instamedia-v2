import { NextRequest, NextResponse } from "next/server";
import { runStudioGenerate } from "@/lib/agents/studio-graph";

export async function POST(req: NextRequest) {
    try {
        const data = await req.json();

        const result = await runStudioGenerate({
            brandId: data.brand_id ?? "default",
            ideaTitle: data.idea_title ?? "",
            ideaHook: data.idea_hook ?? "",
            angle: data.angle ?? "storytelling",
            platform: data.platform ?? "Instagram",
        });

        if (result.error) {
            return NextResponse.json(
                { success: false, error: result.error },
                { status: 500 }
            );
        }

        return NextResponse.json({
            success: true,
            result: result.generatedPost,
        });
    } catch (e) {
        return NextResponse.json(
            { success: false, error: (e as Error).message },
            { status: 500 }
        );
    }
}
