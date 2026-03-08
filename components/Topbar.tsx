"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";

const PAGE_TITLE: Record<string, string> = {
    "/": "Overview",
    "/brand-dna": "Brand DNA",
    "/ideation": "Ideation",
    "/studio": "Creative Studio",
    "/calendar": "Calendar",
    "/connections": "Platform Connections",
    "/database": "Database Expansion",
    "/drift": "Brand Drift Detection",
    "/cold-start": "Cold Start Bootstrap",
    "/analytics": "Analytics Dashboard",
    "/ads": "ADs Manager",
};

export default function Topbar() {
    const pathname = usePathname();
    const title = PAGE_TITLE[pathname] || "InstaMedia";

    return (
        <div className="topbar">
            <div className="topbar-title">{title}</div>
            <div className="topbar-actions">
                {pathname !== "/studio" && (
                    <Link href="/studio" style={{ textDecoration: 'none' }}>
                        <button className="btn btn-primary btn-sm">
                            + New Post
                        </button>
                    </Link>
                )}
            </div>
        </div>
    );
}
