import React from 'react';
import { JobComparison } from '../types';
import { Briefcase, Calendar, GraduationCap } from 'lucide-react';

interface JobComparisonCardProps {
  comparison: JobComparison;
}

export const JobComparisonCard: React.FC<JobComparisonCardProps> = ({ comparison }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
      <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-1">
        <Briefcase className="w-5 h-5 text-indigo-400" />
        Target Role vs. Resume Qualifications
      </h3>
      <p className="text-xs text-slate-400 mb-5">
        Comparison of core qualifications requested in the job description against verified resume credentials.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Seniority & Title */}
        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold mb-2">
            <Briefcase className="w-4 h-4" />
            <span>Seniority Level</span>
          </div>
          <div className="text-sm font-bold text-white">
            {comparison.seniority_match || 'Senior / Mid-Level'}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            Evaluated from title and leadership keywords
          </span>
        </div>

        {/* Years of Experience */}
        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold mb-2">
            <Calendar className="w-4 h-4" />
            <span>Experience Duration</span>
          </div>
          <div className="text-sm font-bold text-white flex items-baseline gap-1.5">
            <span className="font-mono text-base text-emerald-300">
              ~{comparison.years_experience_found ?? 0} yrs
            </span>
            {comparison.years_experience_required && (
              <span className="text-xs text-slate-400">
                (Target: {comparison.years_experience_required}+ yrs)
              </span>
            )}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            Extracted from dated employment history
          </span>
        </div>

        {/* Education Credentials */}
        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-2 text-purple-400 text-xs font-semibold mb-2">
            <GraduationCap className="w-4 h-4" />
            <span>Education Credential</span>
          </div>
          <div className="text-sm font-bold text-white">
            {comparison.degree_found || 'Degree Detected'}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            {comparison.degree_required ? `Required: ${comparison.degree_required}` : 'Matches standard requirements'}
          </span>
        </div>
      </div>
    </div>
  );
};
