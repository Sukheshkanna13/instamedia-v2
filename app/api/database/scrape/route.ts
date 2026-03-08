import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    try {
        const data = await req.json();
        const keywords = data.keywords?.trim() || "";
        const count = Math.min(Number(data.count) || 20, 100);

        if (!keywords) {
            return NextResponse.json({ error: "Keywords required" }, { status: 400 });
        }

        // Return a mock response since Apify is pending Phase 5 integration
        const mockPosts = Array.from({ length: Math.min(count, 5) }).map((_, i) => ({
            id: `mock_${Date.now()}_${i}`,
            text: `[MOCK] Apify scraping for "${keywords}". Integration planned for later phase.`,
            ers: Math.floor(Math.random() * 50) + 40,
            platform: "instagram",
            likes: Math.floor(Math.random() * 1000),
            comments: Math.floor(Math.random() * 100),
            shares: Math.floor(Math.random() * 50),
        }));

        return NextResponse.json({
            success: true,
            message: "Apify integration pending. Using mock data.",
            scraped_posts: mockPosts,
            added_count: 0,
            mode: "mock"
        });

    } catch (e: any) {
        return NextResponse.json(
            { success: false, error: e.message || "Failed to scrape database" },
            { status: 500 }
        );
    }
}
