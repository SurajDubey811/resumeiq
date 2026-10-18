import React, { useState } from 'react';
import { KeywordAnalysis } from '../types';
import { CheckCircle2, AlertCircle, HelpCircle, Sparkles } from 'lucide-react';

interface KeywordExplorerProps {
  analysis: KeywordAnalysis;
}

export const KeywordExplorer: React.FC<KeywordExplorerProps> = ({ analysis }) => {
  const [filter, setFilter] = useState<'all' | 'exact' | 'synonym' | 'missing_req' | 'missing_pref'>('all');

  const totalMatched = analysis.matched_exact.length + analysis.matched_synonyms.length;
  const matchRate = analysis.total_jd_keywords > 0
    ? Math.round((totalMatched / analysis.total_jd_keywords) * 100)
    : 100;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            Keyword & Skill Alignment Explorer
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Exact keyword matches, recognized industry synonyms, and missing qualifications from the job posting.
          </p>
        </div>

        {analysis.total_jd_keywords > 0 && (
          <div className="flex items-center gap-3 bg-slate-800/80 px-4 py-2 rounded-lg border border-slate-700/60 text-sm">
            <span className="text-slate-300">Coverage:</span>
            <span className="font-bold text-emerald-400 font-mono text-base">
              {matchRate}%
            </span>
            <span className="text-xs text-slate-400">
              ({totalMatched}/{analysis.total_jd_keywords} skills)
            </span>
          </div>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 mb-6 border-b border-slate-800 pb-3">
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            filter === 'all'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
        >
          All Skills ({analysis.total_jd_keywords || analysis.matched_exact.length})
        </button>

        <button
          onClick={() => setFilter('exact')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1.5 ${
            filter === 'exact'
              ? 'bg-emerald-600 text-white shadow-sm'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
        >
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          Matched Exact ({analysis.matched_exact.length})
        </button>

        {analysis.matched_synonyms.length > 0 && (
          <button
            onClick={() => setFilter('synonym')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1.5 ${
              filter === 'synonym'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            Matched via Synonyms ({analysis.matched_synonyms.length})
          </button>
        )}

        {analysis.missing_required.length > 0 && (
          <button
            onClick={() => setFilter('missing_req')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1.5 ${
              filter === 'missing_req'
                ? 'bg-rose-600 text-white shadow-sm'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
            Missing Required ({analysis.missing_required.length})
          </button>
        )}

        {analysis.missing_preferred.length > 0 && (
          <button
            onClick={() => setFilter('missing_pref')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1.5 ${
              filter === 'missing_pref'
                ? 'bg-purple-600 text-white shadow-sm'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5 text-purple-400" />
            Missing Preferred ({analysis.missing_preferred.length})
          </button>
        )}
      </div>

      {/* Keyword Chips Grid */}
      <div className="flex flex-wrap gap-2.5 min-h-[100px] content-start">
        {/* Exact Matches */}
        {(filter === 'all' || filter === 'exact') &&
          analysis.matched_exact.map((k, i) => (
            <div
              key={`exact-${i}`}
              className="inline-flex items-center gap-1.5 bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 px-3 py-1.5 rounded-lg text-xs font-medium"
              title={`Found ${k.frequency_in_resume} time(s) in resume`}
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
              <span>{k.skill}</span>
              {k.frequency_in_resume > 1 && (
                <span className="text-[10px] bg-emerald-500/20 px-1.5 py-0.2 rounded text-emerald-200">
                  {k.frequency_in_resume}x
                </span>
              )}
            </div>
          ))}

        {/* Synonym Matches */}
        {(filter === 'all' || filter === 'synonym') &&
          analysis.matched_synonyms.map((k, i) => (
            <div
              key={`syn-${i}`}
              className="inline-flex items-center gap-1.5 bg-blue-950/40 border border-blue-500/30 text-blue-300 px-3 py-1.5 rounded-lg text-xs font-medium"
              title={`Matched via synonym '${k.matched_via}' in resume`}
            >
              <Sparkles className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
              <span>{k.skill}</span>
              <span className="text-[10px] text-blue-400/80 bg-blue-500/10 px-1 rounded">
                via {k.matched_via}
              </span>
            </div>
          ))}

        {/* Missing Required */}
        {(filter === 'all' || filter === 'missing_req') &&
          analysis.missing_required.map((k, i) => (
            <div
              key={`mis-req-${i}`}
              className="inline-flex items-center gap-1.5 bg-rose-950/40 border border-rose-500/30 text-rose-300 px-3 py-1.5 rounded-lg text-xs font-medium"
              title="Required skill missing from resume"
            >
              <AlertCircle className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
              <span>{k.skill}</span>
              <span className="text-[10px] uppercase font-bold text-rose-400 bg-rose-500/20 px-1 rounded">
                Required
              </span>
            </div>
          ))}

        {/* Missing Preferred */}
        {(filter === 'all' || filter === 'missing_pref') &&
          analysis.missing_preferred.map((k, i) => (
            <div
              key={`mis-pref-${i}`}
              className="inline-flex items-center gap-1.5 bg-purple-950/30 border border-purple-500/30 text-purple-300 px-3 py-1.5 rounded-lg text-xs font-medium"
              title="Preferred skill missing from resume"
            >
              <HelpCircle className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
              <span>{k.skill}</span>
              <span className="text-[10px] text-purple-400/80 bg-purple-500/10 px-1 rounded">
                Preferred
              </span>
            </div>
          ))}
      </div>

      {/* Other Skills Section */}
      {analysis.other_resume_skills.length > 0 && (
        <div className="mt-6 pt-5 border-t border-slate-800">
          <h4 className="text-xs uppercase font-bold tracking-wider text-slate-400 mb-2.5">
            Additional Candidate Skills Detected
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {analysis.other_resume_skills.map((skill, i) => (
              <span
                key={i}
                className="text-xs bg-slate-800/80 text-slate-300 border border-slate-700/50 px-2.5 py-1 rounded-md"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
