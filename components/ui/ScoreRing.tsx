"use client";

export default function ScoreRing({ score, size = 80 }: { score: number; size?: number }) {
    const radius = (size - 8) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;
    const color =
        score >= 75
            ? "var(--emerald)"
            : score >= 50
                ? "var(--teal)"
                : score >= 30
                    ? "var(--amber)"
                    : "var(--coral)";

    return (
        <div style={{ position: "relative", width: size, height: size }}>
            <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
                <circle
                    cx={size / 2} cy={size / 2} r={radius}
                    fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={4}
                />
                <circle
                    cx={size / 2} cy={size / 2} r={radius}
                    fill="none" stroke={color} strokeWidth={4}
                    strokeDasharray={circumference} strokeDashoffset={offset}
                    strokeLinecap="round"
                    style={{ transition: "stroke-dashoffset 0.8s ease" }}
                />
            </svg>
            <div style={{
                position: "absolute", inset: 0,
                display: "flex", flexDirection: "column",
                alignItems: "center", justifyContent: "center",
            }}>
                <div style={{
                    fontFamily: "var(--font-display)", fontSize: size * 0.3,
                    fontWeight: 900, color, lineHeight: 1,
                }}>{score}</div>
                <div className="mono-label" style={{ fontSize: 7, marginTop: 2 }}>ERS</div>
            </div>
        </div>
    );
}
