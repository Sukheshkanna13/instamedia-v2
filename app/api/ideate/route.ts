import { NextRequest, NextResponse } from "next/server";
import { runIdeation } from "@/lib/agents/ideation-graph";

export async function POST(req: NextRequest) {
    try {
        const data = await req.json();
        const brandId = data.brand_id ?? "default";
        const focusArea = data.focus_area ?? "general brand storytelling";

        const result = await runIdeation(brandId, focusArea);

        if (result.error) {
            return NextResponse.json(
                { success: false, error: result.error },
                { status: 500 }
            );
        }

        return NextResponse.json({
            success: true,
            result: { ideas: result.ideas },
        });
    } catch (e) {
        return NextResponse.json(
            { success: false, error: (e as Error).message },
            { status: 500 }
        );
    }
}
