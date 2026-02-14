interface ScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
}

const scoreColor = (s: number) => {
  if (s >= 80) return "#34d399";
  if (s >= 60) return "#00d4b8";
  if (s >= 40) return "#f5a623";
  return "#ff5757";
};

export default function ScoreRing({ score, size = 110, strokeWidth = 7 }: ScoreRingProps) {
  const r   = (size / 2) - strokeWidth - 2;
  const circ = 2 * Math.PI * r;
  const fill  = (score / 100) * circ;
  const color = scoreColor(score);

  return (
    <div className="score-ring-container">
      <div className="score-ring" style={{ width: size, height: size }}>
        <svg width={size} height={size}>
          <circle cx={size/2} cy={size/2} r={r}
            fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={strokeWidth} />
          <circle cx={size/2} cy={size/2} r={r}
            fill="none" stroke={color} strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={`${fill} ${circ}`}
            style={{
              transform: `rotate(-90deg)`,
              transformOrigin: "center",
              filter: `drop-shadow(0 0 6px ${color}80)`,
              transition: "stroke-dasharray 0.9s cubic-bezier(0.16,1,0.3,1)"
            }}
          />
        </svg>
        <div className="score-ring-inner">
          <span className="score-num" style={{ color }}>{score}</span>
          <span className="score-denom">/100</span>
        </div>
      </div>
    </div>
  );
}
