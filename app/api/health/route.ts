import { NextResponse } from "next/server";
import { createServerSupabase } from "@/lib/supabase";

export async function GET() {
    const supabase = createServerSupabase();

    let supabaseConnected = false;
    let postCount = 0;

    if (supabase) {
        try {
            const { count } = await supabase
                .from("posts_embeddings")
                .select("*", { count: "exact", head: true });
            supabaseConnected = true;
            postCount = count ?? 0;
        } catch {
            supabaseConnected = false;
        }
    }

    return NextResponse.json({
        status: "online",
        framework: "nextjs",
        ai_engine: "langgraph",
        posts_in_db: postCount,
        llm_provider: process.env.LLM_PROVIDER || "gemini",
        supabase_connected: supabaseConnected,
    });
}
