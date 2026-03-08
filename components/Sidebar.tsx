"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
    {
        section: "Workspace",
        items: [
            { id: "overview", label: "Overview", icon: "◆", href: "/" },
        ]
    },
    {
        section: "Create",
        items: [
            { id: "dna", label: "Brand DNA Vault", icon: "🧬", href: "/brand-dna" },
            { id: "ideation", label: "Ideation", icon: "✦", href: "/ideation" },
            { id: "studio", label: "Creative Studio", icon: "⚡", href: "/studio" },
            { id: "ads_manager", label: "ADs Manager", icon: "🎯", href: "/ads" },
        ]
    },
    {
        section: "Publish",
        items: [
            { id: "calendar", label: "Calendar", icon: "📅", href: "/calendar" },
            { id: "connections", label: "Connections", icon: "🔗", href: "/connections" },
        ]
    },
    {
        section: "Intelligence",
        items: [
            { id: "analytics", label: "Analytics", icon: "📈", href: "/analytics" },
            { id: "database", label: "Database", icon: "🗄️", href: "/database" },
            { id: "drift", label: "Brand Drift", icon: "📊", href: "/drift" },
            { id: "coldstart", label: "Cold Start", icon: "🎯", href: "/cold-start" },
        ]
    }
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="logo-glyph">IM</div>
                <div className="logo-wordmark">
                    <span className="logo-name">InstaMedia</span>
                    <span className="logo-tagline">AI · v3.0</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                {NAV.map(group => (
                    <div key={group.section}>
                        <div className="nav-section-label">{group.section}</div>
                        {group.items.map(item => {
                            const isActive = item.href === "/"
                                ? pathname === "/"
                                : pathname.startsWith(item.href);

                            return (
                                <Link
                                    key={item.id}
                                    href={item.href}
                                    className={`nav-item ${isActive ? "active" : ""}`}
                                    style={{ textDecoration: 'none' }}
                                >
                                    <span className="nav-icon">{item.icon}</span>
                                    {item.label}
                                </Link>
                            );
                        })}
                    </div>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="status-pill">
                    <div className="status-dot" />
                    <span>AI Engine Online</span>
                </div>
                <div style={{ marginTop: 10, fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text-muted)" }}>
                    ESG Prototype v3.0 · LangGraph
                </div>
            </div>
        </aside>
    );
}
