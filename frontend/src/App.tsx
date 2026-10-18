import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { ScoreGauge } from './components/ScoreGauge';
import { DimensionCard } from './components/DimensionCard';
import { KeywordExplorer } from './components/KeywordExplorer';
import { ActionItemsList } from './components/ActionItemsList';
import { JobComparisonCard } from './components/JobComparisonCard';
import { ExtractionReviewModal } from './components/ExtractionReviewModal';
import { ResumeImprovementStudio } from './components/ResumeImprovementStudio';
import { ParsedResume, ATSScorecard } from './types';
import { parseResume, analyzeResume } from './services/api';
import {
  UploadCloud,
  FileText,
  Briefcase,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Download,
  RotateCcw,
  Sliders,
  FileCheck2,
} from 'lucide-react';

const SAMPLE_RESUME_TEXT = `Alex Mercer
alex.mercer@example.com | (555) 987-6543 | linkedin.com/in/alexmercer | github.com/alexmercer
New York, NY

Professional Summary
Results-driven Senior Full Stack Engineer with 6+ years of experience building high-scale distributed systems and cloud-native applications.

Technical Skills
Python, FastAPI, TypeScript, React, Docker, Kubernetes, AWS, PostgreSQL, Redis, CI/CD, Git

Work Experience
Senior Software Engineer - CloudScale Inc. (2021 - Present)
• Architected cloud-native microservices using FastAPI and Docker, reducing API response latency by 35%.
• Spearheaded database query optimization for PostgreSQL and Redis, saving $40,000 in monthly infrastructure expenses.
• Led a distributed team of 6 engineers to launch a real-time event streaming pipeline processing 15M daily requests.

Software Engineer - NextGen Apps (2018 - 2021)
• Developed responsive web user interfaces in React and TypeScript, boosting customer conversion by 22%.
• Automated continuous integration and deployment with GitHub Actions, cutting release cycles from 3 days to 4 hours.

Education
Bachelor of Science in Computer Science - Columbia University (2018)`;

const SAMPLE_JD_TEXT = `Job Title: Senior Backend Engineer

Requirements:
• 5+ years of experience in backend software engineering
• Strong proficiency in Python, FastAPI, and PostgreSQL
• Experience with container orchestration using Kubernetes (or k8s) and Docker
• Demonstrated experience deploying systems on AWS cloud infrastructure
• Bachelor's degree in Computer Science or related engineering discipline

Preferred Qualifications:
• Familiarity with Redis in-memory caching and message queues
• Experience with TypeScript or modern frontend frameworks`;

export const App: React.FC = () => {
  const [view, setView] = useState<'home' | 'results' | 'studio'>('home');
  const [file, setFile] = useState<File | null>(null);
  const [parsedResume, setParsedResume] = useState<ParsedResume | null>(null);
  const [resumeText, setResumeText] = useState<string>('');
  const [jobDescription, setJobDescription] = useState<string>('');
  const [isResumeOnly, setIsResumeOnly] = useState<boolean>(false);
  const [scorecard, setScorecard] = useState<ATSScorecard | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingStep, setLoadingStep] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [showReviewModal, setShowReviewModal] = useState<boolean>(false);

  // Drag and drop state
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelected = async (selectedFile: File) => {
    setError(null);
    const validExtensions = ['.pdf', '.docx'];
    const hasValidExt = validExtensions.some((ext) => selectedFile.name.toLowerCase().endsWith(ext));

    if (!hasValidExt) {
      setError('Invalid file format. Please upload a PDF (.pdf) or Word (.docx) document.');
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File exceeds 10MB limit. Please upload a smaller document.');
      return;
    }

    setFile(selectedFile);
    setLoading(true);
    setLoadingStep('Extracting text and structure from resume document...');

    try {
      const parsed = await parseResume(selectedFile);
      setParsedResume(parsed);
      setResumeText(parsed.raw_text);
      setShowReviewModal(true);
    } catch (err: any) {
      setError(err.message || 'Failed to extract text from resume.');
    } finally {
      setLoading(false);
      setLoadingStep('');
    }
  };

  const handleLoadSample = () => {
    setError(null);
    setResumeText(SAMPLE_RESUME_TEXT);
    setJobDescription(SAMPLE_JD_TEXT);
    setParsedResume({
      filename: 'alex_mercer_resume.pdf',
      file_type: 'pdf',
      page_count: 1,
      word_count: SAMPLE_RESUME_TEXT.split(/\s+/).length,
      raw_text: SAMPLE_RESUME_TEXT,
      contact_info: {
        email: 'alex.mercer@example.com',
        phone: '(555) 987-6543',
        linkedin: 'https://linkedin.com/in/alexmercer',
        github: 'https://github.com/alexmercer',
        location: 'New York, NY',
      },
      sections: [],
      is_scanned_pdf: false,
      ocr_recommended: false,
      warnings: [],
    });
  };

  const runAnalysis = async (confirmedText?: string) => {
    setError(null);
    const textToAnalyze = confirmedText || resumeText;

    if (!textToAnalyze.trim()) {
      setError('Please upload a resume or paste resume text to analyze.');
      return;
    }

    if (!isResumeOnly && !jobDescription.trim()) {
      setError('Please supply a job description, or toggle Resume-Only Mode for general ATS health checking.');
      return;
    }

    setLoading(true);
    setLoadingStep(
      isResumeOnly
        ? 'Running general ATS formatting & structural compliance heuristics...'
        : 'Analyzing keyword matches, experience duration, and qualification alignment...'
    );

    try {
      const result = await analyzeResume(
        textToAnalyze,
        isResumeOnly ? undefined : jobDescription,
        parsedResume?.filename || (file ? file.name : 'resume.pdf'),
        parsedResume || undefined
      );
      setScorecard(result);
      setView('results');
    } catch (err: any) {
      setError(err.message || 'ATS analysis failed.');
    } finally {
      setLoading(false);
      setLoadingStep('');
    }
  };

  const handleDownloadReport = () => {
    if (!scorecard) return;
    const reportData = JSON.stringify(scorecard, null, 2);
    const blob = new Blob([reportData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ResumeIQ_Report_${scorecard.overall_score}pts.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans antialiased">
      <Navbar
        onNewAnalysis={() => {
          setView('home');
          setError(null);
        }}
        activeView={view}
        onViewChange={(v) => setView(v)}
        canViewResults={scorecard !== null}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Notification */}
        {error && (
          <div className="mb-6 p-4 bg-rose-950/40 border border-rose-500/40 rounded-xl flex items-start gap-3 text-sm text-rose-200 animate-fade-in shadow-md">
            <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <span className="font-semibold block">Analysis Notice</span>
              <span>{error}</span>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-rose-400 hover:text-rose-200 text-xs font-semibold"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* VIEW: HOME / UPLOAD */}
        {view === 'home' && (
          <div className="space-y-8 animate-fade-in">
            {/* Hero Header */}
            <div className="text-center max-w-3xl mx-auto space-y-3 pt-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-semibold text-indigo-400">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Deterministic ATS Scoring • Zero Guesswork</span>
              </div>
              <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
                Optimize Your Resume for <span className="text-indigo-400">ATS Algorithms</span>
              </h1>
              <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
                Receive an explainable 100-point compatibility score, uncover missing technical skills, verify formatting safety, and strengthen bullet points with evidence.
              </p>
              
              <div className="pt-2 flex justify-center">
                <button
                  onClick={handleLoadSample}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold underline underline-offset-4 flex items-center gap-1.5 transition"
                >
                  <FileCheck2 className="w-4 h-4" />
                  <span>Click to Load Sample Senior Engineer Resume & Job Description</span>
                </button>
              </div>
            </div>

            {/* Ingestion & Job Input Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
              {/* Column 1: Resume Upload */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-base font-bold text-white flex items-center gap-2">
                      <FileText className="w-5 h-5 text-indigo-400" />
                      1. Upload Resume
                    </h2>
                    <span className="text-[11px] text-slate-500">PDF or DOCX (Max 10 MB)</span>
                  </div>

                  {/* Drag and Drop Box */}
                  <div
                    onDragOver={(e) => {
                      e.preventDefault();
                      setIsDragging(true);
                    }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={handleFileDrop}
                    className={`border-2 border-dashed rounded-xl p-8 text-center transition flex flex-col items-center justify-center cursor-pointer ${
                      isDragging
                        ? 'border-indigo-500 bg-indigo-500/10'
                        : file || resumeText
                        ? 'border-emerald-500/50 bg-emerald-950/10'
                        : 'border-slate-800 hover:border-slate-700 bg-slate-950/40'
                    }`}
                    onClick={() => document.getElementById('resume-file-input')?.click()}
                  >
                    <input
                      id="resume-file-input"
                      type="file"
                      accept=".pdf,.docx"
                      className="hidden"
                      onChange={(e) => e.target.files?.[0] && handleFileSelected(e.target.files[0])}
                    />

                    {file || resumeText ? (
                      <div className="space-y-2">
                        <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
                          <CheckCircle2 className="w-6 h-6" />
                        </div>
                        <p className="font-semibold text-white text-sm">
                          {file ? file.name : parsedResume?.filename || 'Resume Loaded'}
                        </p>
                        <p className="text-xs text-slate-400 font-mono">
                          {parsedResume?.word_count ?? resumeText.split(/\s+/).length} words extracted
                        </p>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setShowReviewModal(true);
                          }}
                          className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold underline underline-offset-2"
                        >
                          Review & Edit Extracted Text
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <div className="w-12 h-12 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
                          <UploadCloud className="w-6 h-6" />
                        </div>
                        <p className="font-semibold text-white text-sm">
                          Drag and drop your resume file here
                        </p>
                        <p className="text-xs text-slate-500">
                          or click to browse from your device
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Manual Paste / Edit Toggle */}
                  <div className="mt-4">
                    <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                      Or Paste Resume Plain Text:
                    </label>
                    <textarea
                      rows={6}
                      value={resumeText}
                      onChange={(e) => setResumeText(e.target.value)}
                      placeholder="Paste resume content here if you prefer not to upload a file..."
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                    />
                  </div>
                </div>

                {/* Privacy Guarantee Note */}
                <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center gap-2 text-xs text-slate-400">
                  <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Processed ephemerally in-memory. Zero document retention.</span>
                </div>
              </div>

              {/* Column 2: Job Description Input */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-base font-bold text-white flex items-center gap-2">
                      <Briefcase className="w-5 h-5 text-indigo-400" />
                      2. Target Job Description
                    </h2>

                    {/* Resume Only Mode Switch */}
                    <label className="flex items-center gap-2 cursor-pointer bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 hover:border-slate-700 transition">
                      <input
                        type="checkbox"
                        checked={isResumeOnly}
                        onChange={(e) => setIsResumeOnly(e.target.checked)}
                        className="w-3.5 h-3.5 rounded text-indigo-600 focus:ring-indigo-500 bg-slate-900 border-slate-700"
                      />
                      <span className="text-xs text-slate-300 font-medium select-none">
                        Resume-Only Mode
                      </span>
                    </label>
                  </div>

                  {isResumeOnly ? (
                    <div className="p-6 bg-slate-950/60 border border-indigo-500/20 rounded-xl text-center space-y-2 my-6">
                      <Sliders className="w-8 h-8 text-indigo-400 mx-auto" />
                      <h3 className="text-sm font-bold text-white">General ATS Health Mode Active</h3>
                      <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                        Measures general ATS formatting compliance, bullet action verbs, quantifiable metrics, and section structure rather than job-specific keyword fit.
                      </p>
                    </div>
                  ) : (
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                        Job Posting Text (Responsibilities & Qualifications):
                      </label>
                      <textarea
                        rows={13}
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                        placeholder="Paste the full job posting here (Title, Requirements, Qualifications, Responsibilities)..."
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                      />
                    </div>
                  )}
                </div>

                {/* Primary CTA Button */}
                <div className="mt-6 pt-4 border-t border-slate-800/80">
                  <button
                    onClick={() => runAnalysis()}
                    disabled={loading}
                    className="w-full py-3.5 px-6 rounded-xl font-bold text-sm bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/25 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>{loadingStep || 'Analyzing...'}</span>
                      </>
                    ) : (
                      <>
                        <span>Analyze Resume Compatibility</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW: RESULTS SCORECARD */}
        {view === 'results' && scorecard && (
          <div className="space-y-8 animate-fade-in">
            {/* Top Scorecard Hero Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-sm">
              <div className="flex flex-col lg:flex-row items-center justify-between gap-8">
                {/* Left: Overall Gauge */}
                <div className="flex-shrink-0">
                  <ScoreGauge score={scorecard.overall_score} tier={scorecard.tier} size={200} />
                </div>

                {/* Center: Score Verdict & Mode */}
                <div className="flex-1 text-center lg:text-left space-y-3">
                  <div className="flex flex-wrap items-center justify-center lg:justify-start gap-2">
                    <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {scorecard.mode === 'job_matched' ? 'Job-Specific Fit' : 'General ATS Health'}
                    </span>
                    <span className="text-xs text-slate-400">
                      Document: <strong>{parsedResume?.filename || 'Resume'}</strong>
                    </span>
                  </div>

                  <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
                    Overall ATS Compatibility: <span className="text-indigo-400">{scorecard.overall_score}/100</span>
                  </h2>

                  <p className="text-xs sm:text-sm text-slate-400 max-w-2xl leading-relaxed">
                    {scorecard.mode_description}
                  </p>

                  {/* Highlights Bar */}
                  <div className="pt-2 flex flex-wrap gap-4 justify-center lg:justify-start text-xs text-slate-300">
                    <div className="flex items-center gap-1.5 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span>{scorecard.strengths.length} Key Strengths Identified</span>
                    </div>
                    <div className="flex items-center gap-1.5 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                      <span>{scorecard.prioritized_action_items.length} Action Items Suggested</span>
                    </div>
                  </div>
                </div>

                {/* Right: Quick Action Controls */}
                <div className="flex flex-col gap-2.5 w-full sm:w-auto">
                  <button
                    onClick={() => setView('studio')}
                    className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition flex items-center justify-center gap-2 shadow-md shadow-indigo-600/20"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>Improve Sections in Studio</span>
                  </button>

                  <button
                    onClick={handleDownloadReport}
                    className="px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 transition flex items-center justify-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download Report (JSON)</span>
                  </button>

                  <button
                    onClick={() => setView('home')}
                    className="px-5 py-2.5 rounded-xl text-slate-400 hover:text-white text-xs font-medium transition flex items-center justify-center gap-1.5"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Scan Another Resume</span>
                  </button>
                </div>
              </div>
            </div>

            {/* ATS Readability Warnings if present */}
            {scorecard.ats_formatting_warnings.length > 0 && (
              <div className="p-4 bg-amber-950/20 border border-amber-500/30 rounded-xl flex items-start gap-3 text-xs text-amber-200">
                <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <span className="font-semibold block mb-0.5">Formatting & Layout Warnings:</span>
                  <ul className="list-disc list-inside space-y-0.5 text-amber-300">
                    {scorecard.ats_formatting_warnings.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Target Job Comparison Widget (if JD provided) */}
            {scorecard.job_comparison && (
              <JobComparisonCard comparison={scorecard.job_comparison} />
            )}

            {/* Keyword Explorer */}
            <KeywordExplorer analysis={scorecard.keyword_analysis} />

            {/* Category Breakdown Cards */}
            <div>
              <div className="mb-4">
                <h3 className="text-lg font-bold text-white">Score Breakdown by Category</h3>
                <p className="text-xs text-slate-400">
                  Click any category to inspect evidence found in your resume, point deductions, and actionable fixes.
                </p>
              </div>

              <div className="space-y-3">
                {Object.values(scorecard.dimension_scores).map((dim) => (
                  <DimensionCard key={dim.key} score={dim} />
                ))}
              </div>
            </div>

            {/* Prioritized Action Items */}
            <ActionItemsList
              items={scorecard.prioritized_action_items}
              onImproveClick={() => setView('studio')}
            />
          </div>
        )}

        {/* VIEW: IMPROVEMENT STUDIO */}
        {view === 'studio' && (
          <ResumeImprovementStudio
            resumeText={resumeText}
            jobDescription={isResumeOnly ? undefined : jobDescription}
            sections={parsedResume?.sections}
            onBack={() => setView('results')}
          />
        )}
      </main>

      {/* Review Modal */}
      {parsedResume && (
        <ExtractionReviewModal
          parsedResume={parsedResume}
          isOpen={showReviewModal}
          onClose={() => setShowReviewModal(false)}
          onConfirm={(updatedText) => {
            setResumeText(updatedText);
            setShowReviewModal(false);
            runAnalysis(updatedText);
          }}
        />
      )}

      <Footer />
    </div>
  );
};

export default App;
