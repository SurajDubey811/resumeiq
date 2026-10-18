import React from 'react';
import { ShieldCheck, Lock, Code2 } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800 bg-slate-950 mt-auto py-8 text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className="font-bold text-slate-300">ResumeIQ</span>
          <span>— Explainable ATS Resume Compatibility & Optimization Engine</span>
        </div>

        <div className="flex flex-wrap items-center gap-6">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Lock className="w-3.5 h-3.5 text-emerald-400" />
            <span>In-Memory Processing • No Database Retention</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
            <span>Deterministic Heuristic Engine (Layer A)</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <Code2 className="w-3.5 h-3.5 text-purple-400" />
            <span>PDF & DOCX Support (Max 10 MB)</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
