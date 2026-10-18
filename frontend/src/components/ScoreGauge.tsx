import React from 'react';

interface ScoreGaugeProps {
  score: number;
  tier: 'Strong' | 'Good' | 'Fair' | 'Needs Improvement';
  size?: number;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({ score, tier, size = 180 }) => {
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.max(0, Math.min(100, score));
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

  const getTierColors = () => {
    switch (tier) {
      case 'Strong':
        return {
          stroke: '#22c55e',
          text: 'text-emerald-400',
          bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        };
      case 'Good':
        return {
          stroke: '#3b82f6',
          text: 'text-blue-400',
          bg: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
        };
      case 'Fair':
        return {
          stroke: '#f59e0b',
          text: 'text-amber-400',
          bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        };
      case 'Needs Improvement':
      default:
        return {
          stroke: '#ef4444',
          text: 'text-rose-400',
          bg: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
        };
    }
  };

  const colors = getTierColors();

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        <svg className="transform -rotate-90" width={size} height={size}>
          {/* Background circle track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#1e293b"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        
        {/* Centered Score */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-5xl font-extrabold tracking-tight text-white font-mono">
            {clampedScore}
          </span>
          <span className="text-xs uppercase font-medium tracking-wider text-slate-400">
            out of 100
          </span>
        </div>
      </div>

      <div className={`mt-3 px-3 py-1 rounded-full text-xs font-semibold border ${colors.bg}`}>
        {tier}
      </div>
    </div>
  );
};
