import { NextResponse } from "next/server";
import { createServerSupabase } from "@/lib/supabase";

export async function GET() {
    const supabase = createServerSupabase();

    if (!supabase) {
        return NextResponse.json(
            { error: "Supabase not configured locally" },
            { status: 503 }
        );
    }

    try {
        // Fetch all posts to calculate metrics
        const { data: posts, error } = await supabase
            .from("posts_embeddings")
            .select("content, platform, ers, likes, comments, shares")
            .order("ers", { ascending: false });

        if (error) throw error;

        if (!posts || posts.length === 0) {
            return NextResponse.json(
                {
                    total_posts: 0,
                    avg_ers: 0,
                    max_ers: 0,
                    min_ers: 0,
                    top_posts: [],
                },
                { status: 200 }
            );
        }

        const ersScores = posts.map(p => p.ers || 0);
        const sumErs = ersScores.reduce((acc, val) => acc + val, 0);
        const avgErs = Number((sumErs / ersScores.length).toFixed(2));
        const maxErs = Number(Math.max(...ersScores).toFixed(2));
        const minErs = Number(Math.min(...ersScores).toFixed(2));

        const topPosts = posts.slice(0, 10).map(p => ({
            text: p.content ? p.content.slice(0, 120) + "..." : "No text",
            ers: p.ers || 0,
            platform: p.platform || "unknown",
        }));

        return NextResponse.json({
            total_posts: posts.length,
            avg_ers: avgErs,
            max_ers: maxErs,
            min_ers: minErs,
            top_posts: topPosts,
        });

    } catch (e: any) {
        return NextResponse.json(
            { error: e.message || "Failed to fetch stats" },
            { status: 500 }
        );
    }
}
