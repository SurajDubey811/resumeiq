import React, { useState } from 'react';
import { ImprovementSuggestion, ExtractedSection } from '../types';
import { improveResume } from '../services/api';
import { Check, X, Sparkles, RefreshCw, Copy, CheckCheck, ShieldCheck, Cpu } from 'lucide-react';

interface ResumeImprovementStudioProps {
  resumeText: string;
  jobDescription?: string;
  sections?: ExtractedSection[];
  onBack: () => void;
}

export const ResumeImprovementStudio: React.FC<ResumeImprovementStudioProps> = ({
  resumeText,
  jobDescription,
  sections,
  onBack,
}) => {
  const [useAI, setUseAI] = useState(false);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<ImprovementSuggestion[]>([]);
  const [disclaimer, setDisclaimer] = useState<string>('');
  const [copied, setCopied] = useState(false);

  const fetchSuggestions = async (enableAI: boolean) => {
    setLoading(true);
    try {
      const res = await improveResume(resumeText, jobDescription, sections, enableAI);
      setSuggestions(res.suggestions);
      setDisclaimer(res.disclaimer);
    } catch (err: any) {
      alert(err.message || 'Failed to generate improvement suggestions.');
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch on mount
  React.useEffect(() => {
    fetchSuggestions(useAI);
  }, []);

  const handleStatusChange = (id: string, status: 'accepted' | 'rejected') => {
    setSuggestions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status: s.status === status ? 'pending' : status } : s))
    );
  };

  // Generate updated resume text by replacing accepted suggestions
  const getCompiledResume = () => {
    let result = resumeText;
    for (const sug of suggestions) {
      if (sug.status === 'accepted') {
        result = result.replace(sug.original_text, sug.suggested_text);
      }
    }
    return result;
  };

  const handleCopyCompiled = () => {
    navigator.clipboard.writeText(getCompiledResume());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const acceptedCount = suggestions.filter((s) => s.status === 'accepted').length;

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      {/* Studio Header & Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="p-2 bg-indigo-500/10 text-indigo-400 rounded-lg border border-indigo-500/20">
                <Sparkles className="w-5 h-5" />
              </span>
              <h2 className="text-xl font-bold text-white">Resume Improvement Studio</h2>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Compare original bullet points with evidence-anchored revisions. Accept or reject suggestions individually with zero unearned claim inflation.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* AI Layer Toggle */}
            <label className="flex items-center gap-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl cursor-pointer hover:border-slate-700 transition">
              <input
                type="checkbox"
                checked={useAI}
                onChange={(e) => {
                  const val = e.target.checked;
                  setUseAI(val);
                  fetchSuggestions(val);
                }}
                className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 bg-slate-900 border-slate-700"
              />
              <span className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                Optional AI (Layer B)
              </span>
            </label>

            <button
              onClick={() => fetchSuggestions(useAI)}
              disabled={loading}
              className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-700 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Regenerate</span>
            </button>

            <button
              onClick={onBack}
              className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition"
            >
              Back to Scorecard
            </button>
          </div>
        </div>

        {/* Engine Transparency Disclaimer */}
        {disclaimer && (
          <div className="mt-4 pt-4 border-t border-slate-800/80 flex items-center gap-2 text-xs text-slate-400">
            <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>{disclaimer}</span>
          </div>
        )}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
          <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin mx-auto" />
          <h4 className="text-base font-semibold text-white">Analyzing Bullet Phrasing & Metrics...</h4>
          <p className="text-xs text-slate-400">Evaluating action verbs, quantifiable metrics, and keyword alignment without hallucinating facts.</p>
        </div>
      )}

      {/* Suggestions List */}
      {!loading && suggestions.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-400 px-1">
            <span>
              Showing {suggestions.length} actionable suggestions ({acceptedCount} accepted)
            </span>
            <span>Click Accept to apply revisions to your exportable resume.</span>
          </div>

          {suggestions.map((sug) => {
            const isAccepted = sug.status === 'accepted';
            const isRejected = sug.status === 'rejected';

            return (
              <div
                key={sug.id}
                className={`border rounded-xl p-5 transition bg-slate-900 ${
                  isAccepted
                    ? 'border-emerald-500/50 bg-emerald-950/10'
                    : isRejected
                    ? 'border-slate-800/50 opacity-60'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                {/* Header Tag & Rationale */}
                <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-semibold text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded border border-indigo-500/20">
                      {sug.section}
                    </span>
                    <span className="text-[11px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                      {sug.category}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleStatusChange(sug.id, 'accepted')}
                      className={`px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1 transition ${
                        isAccepted
                          ? 'bg-emerald-600 text-white'
                          : 'bg-slate-800 text-emerald-400 hover:bg-emerald-950/60 border border-emerald-500/30'
                      }`}
                    >
                      <Check className="w-3.5 h-3.5" />
                      <span>{isAccepted ? 'Accepted' : 'Accept'}</span>
                    </button>

                    <button
                      onClick={() => handleStatusChange(sug.id, 'rejected')}
                      className={`px-3 py-1 rounded-lg text-xs font-medium flex items-center gap-1 transition ${
                        isRejected
                          ? 'bg-rose-900/60 text-rose-300 border border-rose-500/30'
                          : 'bg-slate-800 text-slate-400 hover:text-rose-400 hover:bg-slate-750'
                      }`}
                    >
                      <X className="w-3.5 h-3.5" />
                      <span>{isRejected ? 'Declined' : 'Decline'}</span>
                    </button>
                  </div>
                </div>

                {/* Side-by-Side Comparison */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-3 text-xs font-mono">
                  {/* Original */}
                  <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800/80">
                    <span className="text-[10px] font-sans uppercase font-bold text-slate-500 block mb-1.5">
                      Original Text:
                    </span>
                    <p className="text-slate-400 leading-relaxed">{sug.original_text}</p>
                  </div>

                  {/* Suggested */}
                  <div className={`p-3.5 rounded-lg border ${
                    isAccepted ? 'bg-emerald-950/20 border-emerald-500/30' : 'bg-slate-950/80 border-indigo-500/30'
                  }`}>
                    <span className="text-[10px] font-sans uppercase font-bold text-emerald-400 block mb-1.5 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" />
                      ATS Optimized Revision:
                    </span>
                    <p className="text-emerald-200 leading-relaxed font-semibold">{sug.suggested_text}</p>
                  </div>
                </div>

                {/* Explanation */}
                <div className="mt-2 text-xs text-slate-400 bg-slate-950/40 p-2.5 rounded border border-slate-800/60 flex items-start gap-2">
                  <span className="text-indigo-400 font-semibold flex-shrink-0">Why this helps:</span>
                  <span>{sug.rationale}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Compiled Export Bar */}
      {!loading && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h4 className="text-sm font-bold text-white">Export Updated Resume</h4>
            <p className="text-xs text-slate-400 mt-0.5">
              Copy the revised text with your {acceptedCount} accepted improvement(s) incorporated.
            </p>
          </div>

          <button
            onClick={handleCopyCompiled}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow-md shadow-indigo-600/20"
          >
            {copied ? <CheckCheck className="w-4 h-4 text-emerald-300" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? 'Copied to Clipboard!' : 'Copy Revised Resume Text'}</span>
          </button>
        </div>
      )}
    </div>
  );
};
