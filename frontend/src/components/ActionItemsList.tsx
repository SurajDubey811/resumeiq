import React from 'react';
import { ActionItem } from '../types';
import { ArrowUpRight, Zap } from 'lucide-react';

interface ActionItemsListProps {
  items: ActionItem[];
  onImproveClick?: () => void;
}

export const ActionItemsList: React.FC<ActionItemsListProps> = ({ items, onImproveClick }) => {
  if (items.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center">
        <p className="text-emerald-400 font-medium text-sm">
          No critical action items detected! Your resume aligns cleanly with ATS guidelines.
        </p>
      </div>
    );
  }

  const getPriorityBadge = (priority: 'High' | 'Medium' | 'Low') => {
    switch (priority) {
      case 'High':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'Medium':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'Low':
      default:
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-400" />
            Prioritized Improvement Action Items
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Ranked by expected ATS compatibility score impact. Fix High priority items first.
          </p>
        </div>

        {onImproveClick && (
          <button
            onClick={onImproveClick}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition shadow-sm"
          >
            <span>Open Studio</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="space-y-3">
        {items.map((item) => (
          <div
            key={item.id}
            className="p-4 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition"
          >
            <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded text-[11px] font-bold border uppercase tracking-wider ${getPriorityBadge(item.priority)}`}>
                  {item.priority} Priority
                </span>
                <span className="text-xs font-medium text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                  {item.category}
                </span>
              </div>
              <span className="text-xs font-semibold text-slate-200">
                {item.title}
              </span>
            </div>

            <p className="text-xs text-slate-400 mb-2 leading-relaxed">
              {item.explanation}
            </p>

            {item.example_fix && (
              <div className="bg-slate-900/90 border border-slate-800 p-2.5 rounded text-xs text-emerald-300 font-mono">
                <span className="text-slate-500 block text-[10px] uppercase font-sans font-bold mb-0.5">
                  Suggested Action:
                </span>
                {item.example_fix}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
