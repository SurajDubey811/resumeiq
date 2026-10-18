import React from 'react';
import { Target, ShieldCheck, Sparkles } from 'lucide-react';

interface NavbarProps {
  onNewAnalysis: () => void;
  activeView: 'home' | 'results' | 'studio';
  onViewChange: (view: 'home' | 'results' | 'studio') => void;
  canViewResults: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  onNewAnalysis,
  activeView,
  onViewChange,
  canViewResults,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div
          className="flex items-center gap-3 cursor-pointer select-none"
          onClick={onNewAnalysis}
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight text-white">
                Resume<span className="text-indigo-400">IQ</span>
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                ATS Engine
              </span>
            </div>
            <span className="text-[11px] text-slate-400 block -mt-0.5">
              Explainable Compatibility Analyzer
            </span>
          </div>
        </div>

        {/* Center Nav Links */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800 text-xs font-medium">
          <button
            onClick={() => onViewChange('home')}
            className={`px-3.5 py-1.5 rounded-lg transition ${
              activeView === 'home'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Upload & Analyze
          </button>

          {canViewResults && (
            <button
              onClick={() => onViewChange('results')}
              className={`px-3.5 py-1.5 rounded-lg transition ${
                activeView === 'results'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              ATS Scorecard
            </button>
          )}

          {canViewResults && (
            <button
              onClick={() => onViewChange('studio')}
              className={`px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5 ${
                activeView === 'studio'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>Improvement Studio</span>
            </button>
          )}
        </nav>

        {/* Privacy Indicator */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-[11px] font-medium text-slate-300">Zero Retention • Local First</span>
          </div>

          <button
            onClick={onNewAnalysis}
            className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
          >
            New Scan
          </button>
        </div>
      </div>
    </header>
  );
};
