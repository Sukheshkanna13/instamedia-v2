import { NextRequest, NextResponse } from "next/server";
import { runMediaGenerate } from "@/lib/agents/media-graph";

export async function POST(req: NextRequest) {
    try {
        const data = await req.json();

        // Basic validation
        if (!data.caption) {
            return NextResponse.json({ error: "caption is required" }, { status: 400 });
        }

        const validFormats = ["image", "carousel", "video"];
        const format = data.format && validFormats.includes(data.format) ? data.format : "image";

        const result = await runMediaGenerate({
            brandId: data.brand_id ?? "default",
            caption: data.caption,
            hashtags: data.hashtags ?? [],
            format: format as "image" | "carousel" | "video",
            brandContext: data.brand_context ?? "",
        });

        if (result.error) {
            return NextResponse.json(
                { success: false, error: result.error },
                { status: 500 }
            );
        }

        return NextResponse.json({
            success: true,
            result: result.generatedMedia,
        });
    } catch (e: any) {
        return NextResponse.json(
            { success: false, error: e.message || "Unknown error" },
            { status: 500 }
        );
    }
}
