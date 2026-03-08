import { NextRequest, NextResponse } from "next/server";
import { createServerSupabase } from "@/lib/supabase";

export async function POST(req: NextRequest) {
    const supabase = createServerSupabase();
    if (!supabase) {
        return NextResponse.json({ error: "Supabase not configured" }, { status: 503 });
    }

    try {
        const formData = await req.formData();
        const logoFile = formData.get("logo") as File | null;
        const brandId = (formData.get("brand_id") as string) || "default";

        if (!logoFile) {
            return NextResponse.json({ error: "No logo file provided" }, { status: 400 });
        }

        const ext = logoFile.name.split('.').pop()?.toLowerCase();
        if (!ext || !['png', 'jpg', 'jpeg', 'svg', 'webp'].includes(ext)) {
            return NextResponse.json({ error: "Invalid file type" }, { status: 400 });
        }

        const uniqueFilename = `${brandId}_${Date.now()}.${ext}`;

        // Ensure bucket exists (ignores error if already exists)
        await supabase.storage.createBucket('brand-logos', { public: true }).then(() => { }).catch(() => { });

        const arrayBuffer = await logoFile.arrayBuffer();
        const buffer = Buffer.from(arrayBuffer);

        const { error: uploadError } = await supabase.storage.from("brand-logos").upload(
            uniqueFilename,
            buffer,
            { contentType: logoFile.type, upsert: true }
        );

        if (uploadError) throw uploadError;

        const { data: publicData } = supabase.storage.from("brand-logos").getPublicUrl(uniqueFilename);

        // Attempt to update brand_dna (if it exists)
        await supabase.from("brand_dna").update({
            logo_url: publicData.publicUrl,
            updated_at: new Date().toISOString()
        }).eq("brand_id", brandId);

        return NextResponse.json({
            success: true,
            logo_url: publicData.publicUrl,
            message: "Logo uploaded successfully"
        });

    } catch (e: any) {
        return NextResponse.json({ error: e.message || "Upload failed" }, { status: 500 });
    }
}
