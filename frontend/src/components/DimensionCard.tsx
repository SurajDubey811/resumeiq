import React, { useState } from 'react';
import { DimensionScore } from '../types';
import { ChevronDown, ChevronUp, Check, AlertTriangle, ArrowRight } from 'lucide-react';

interface DimensionCardProps {
  score: DimensionScore;
}

export const DimensionCard: React.FC<DimensionCardProps> = ({ score }) => {
  const [expanded, setExpanded] = useState(false);

  const getStatusBadge = () => {
    if (score.score_percentage >= 80) {
      return {
        label: 'Strong',
        badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
        bar: 'bg-emerald-500',
      };
    } else if (score.score_percentage >= 60) {
      return {
        label: 'Good',
        badge: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
        bar: 'bg-blue-500',
      };
    } else {
      return {
        label: 'Needs Attention',
        badge: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
        bar: 'bg-rose-500',
      };
    }
  };

  const status = getStatusBadge();

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden transition hover:border-slate-700/80 shadow-sm">
      <div
        className="p-5 cursor-pointer select-none flex flex-col md:flex-row md:items-center justify-between gap-4"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h4 className="font-semibold text-white text-base">{score.name}</h4>
            <span className={`px-2 py-0.5 rounded-full text-[11px] font-semibold border ${status.badge}`}>
              {status.label}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">{score.summary}</p>
        </div>

        <div className="flex items-center gap-5 justify-between md:justify-end">
          <div className="flex flex-col items-end min-w-[100px]">
            <div className="flex items-baseline gap-1">
              <span className="text-xl font-bold font-mono text-white">
                {score.points_earned}
              </span>
              <span className="text-xs text-slate-400">/ {score.max_points} pts</span>
            </div>
            {/* Progress bar */}
            <div className="w-28 h-1.5 bg-slate-800 rounded-full mt-1.5 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${status.bar}`}
                style={{ width: `${Math.min(100, Math.max(0, score.score_percentage))}%` }}
              />
            </div>
          </div>

          <button
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
            aria-label="Toggle details"
          >
            {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Expanded Accordion Details */}
      {expanded && (
        <div className="px-5 pb-5 pt-2 border-t border-slate-800/80 bg-slate-950/40 space-y-4">
          {/* Supporting Evidence */}
          {score.evidence.length > 0 && (
            <div>
              <h5 className="text-xs uppercase font-bold text-slate-400 tracking-wider mb-2 flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                Evidence Found in Resume
              </h5>
              <ul className="space-y-1.5">
                {score.evidence.map((item, idx) => (
                  <li key={idx} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-900/60 p-2 rounded border border-slate-800">
                    <span className="text-emerald-400 mt-0.5">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Deductions & Gaps */}
          {score.deductions.length > 0 && (
            <div>
              <h5 className="text-xs uppercase font-bold text-rose-400 tracking-wider mb-2 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                Point Deductions & Specific Gaps
              </h5>
              <div className="space-y-2">
                {score.deductions.map((ded, idx) => (
                  <div key={idx} className="bg-rose-950/20 border border-rose-500/20 p-3 rounded-lg text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-rose-300">{ded.reason}</span>
                      <span className="font-mono font-bold text-rose-400 bg-rose-500/10 px-1.5 py-0.5 rounded">
                        -{ded.points_lost} pts
                      </span>
                    </div>
                    <p className="text-slate-400 mb-2">{ded.evidence}</p>
                    <div className="flex items-start gap-1.5 text-emerald-300 bg-emerald-950/30 p-2 rounded border border-emerald-500/20">
                      <ArrowRight className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span><strong>Actionable Fix:</strong> {ded.fix_suggestion}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* General Recommendations if no deductions */}
          {score.deductions.length === 0 && score.recommendations.length > 0 && (
            <div>
              <h5 className="text-xs uppercase font-bold text-slate-400 tracking-wider mb-1.5">
                Suggested Optimizations
              </h5>
              <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
                {score.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
