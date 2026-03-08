import { NextRequest, NextResponse } from "next/server";
import { createServerSupabase } from "@/lib/supabase";

// POST — schedule a post
export async function POST(req: NextRequest) {
    const data = await req.json();
    const supabase = createServerSupabase();

    const record = {
        id: crypto.randomUUID(),
        content: data.content ?? "",
        platform: data.platform ?? "instagram",
        scheduled_time: data.scheduled_time ?? "",
        brand_id: data.brand_id ?? "default",
        resonance_score: data.resonance_score ?? 0,
        image_style: data.image_style ?? "",
        hashtags: JSON.stringify(data.hashtags ?? []),
        status: data.status ?? "scheduled",
        created_at: new Date().toISOString(),
    };

    if (!supabase) {
        return NextResponse.json({ success: true, post: record });
    }

    try {
        await supabase.from("scheduled_posts").insert(record);
        return NextResponse.json({ success: true, post: record });
    } catch (e) {
        return NextResponse.json(
            { error: (e as Error).message },
            { status: 500 }
        );
    }
}

// GET — list calendar posts
export async function GET(req: NextRequest) {
    const brandId = req.nextUrl.searchParams.get("brand_id") ?? "default";
    const supabase = createServerSupabase();

    if (!supabase) {
        return NextResponse.json({ success: true, posts: [] });
    }

    try {
        const { data, error } = await supabase
            .from("scheduled_posts")
            .select("*")
            .eq("brand_id", brandId);

        if (error) throw error;

        return NextResponse.json({
            success: true,
            posts: data ?? [],
        });
    } catch (e) {
        return NextResponse.json(
            { error: (e as Error).message },
            { status: 500 }
        );
    }
}

// DELETE — delete a post
export async function DELETE(req: NextRequest) {
    const postId = req.nextUrl.searchParams.get("id");
    const brandId = req.nextUrl.searchParams.get("brand_id") ?? "default";
    const supabase = createServerSupabase();

    if (!postId) {
        return NextResponse.json({ error: "Post ID required" }, { status: 400 });
    }

    if (!supabase) {
        return NextResponse.json({ success: true, message: "Post deleted" });
    }

    try {
        await supabase
            .from("scheduled_posts")
            .delete()
            .eq("id", postId)
            .eq("brand_id", brandId);

        return NextResponse.json({
            success: true,
            message: "Post deleted from calendar",
        });
    } catch (e) {
        return NextResponse.json(
            { error: (e as Error).message },
            { status: 500 }
        );
    }
}
