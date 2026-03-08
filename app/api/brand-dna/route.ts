import { NextRequest, NextResponse } from "next/server";
import { createServerSupabase } from "@/lib/supabase";

// GET — fetch brand DNA
export async function GET(req: NextRequest) {
    const brandId = req.nextUrl.searchParams.get("brand_id") ?? "default";
    const supabase = createServerSupabase();

    if (!supabase) {
        return NextResponse.json({ success: true, data: {} });
    }

    try {
        const { data, error } = await supabase
            .from("brand_dna")
            .select("*")
            .eq("brand_id", brandId);

        if (error) throw error;

        return NextResponse.json({
            success: true,
            data: data?.[0] ?? {},
        });
    } catch (e) {
        return NextResponse.json(
            { error: (e as Error).message },
            { status: 500 }
        );
    }
}

// POST — save/update brand DNA
export async function POST(req: NextRequest) {
    const data = await req.json();
    const brandId = data.brand_id ?? "default";
    const supabase = createServerSupabase();

    const record = {
        brand_id: brandId,
        brand_name: data.brand_name ?? "",
        mission: data.mission ?? "",
        tone_descriptors: JSON.stringify(data.tone_descriptors ?? []),
        hex_colors: JSON.stringify(data.hex_colors ?? []),
        banned_words: JSON.stringify(data.banned_words ?? []),
        typography: data.typography ?? "",
        logo_url: data.logo_url ?? "",
        connected_platforms: JSON.stringify(data.connected_platforms ?? []),
        updated_at: new Date().toISOString(),
    };

    if (!supabase) {
        return NextResponse.json({
            success: true,
            message: "Brand DNA saved (local mode).",
        });
    }

    try {
        const { data: existing } = await supabase
            .from("brand_dna")
            .select("id")
            .eq("brand_id", brandId);

        if (existing && existing.length > 0) {
            await supabase
                .from("brand_dna")
                .update(record)
                .eq("brand_id", brandId);
        } else {
            await supabase.from("brand_dna").insert({
                ...record,
                id: crypto.randomUUID(),
            });
        }

        return NextResponse.json({
            success: true,
            message: "Brand DNA saved.",
        });
    } catch (e) {
        return NextResponse.json(
            { error: (e as Error).message },
            { status: 500 }
        );
    }
}
