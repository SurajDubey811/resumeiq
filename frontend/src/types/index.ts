export interface ContactInfo {
  email?: string | null;
  phone?: string | null;
  linkedin?: string | null;
  github?: string | null;
  location?: string | null;
  portfolio?: string | null;
}

export interface ExtractedSection {
  name: string;
  raw_title: string;
  content: string;
  bullets: string[];
}

export interface ParsedResume {
  filename: string;
  file_type: 'pdf' | 'docx';
  page_count: number;
  word_count: number;
  raw_text: string;
  contact_info: ContactInfo;
  sections: ExtractedSection[];
  is_scanned_pdf: boolean;
  ocr_recommended: boolean;
  warnings: string[];
}

export interface KeywordItem {
  skill: string;
  category?: string;
  importance: 'required' | 'preferred' | 'general';
  matched: boolean;
  match_type: 'exact' | 'synonym' | 'missing';
  matched_via?: string | null;
  frequency_in_resume: number;
}

export interface KeywordAnalysis {
  total_jd_keywords: number;
  matched_exact: KeywordItem[];
  matched_synonyms: KeywordItem[];
  missing_required: KeywordItem[];
  missing_preferred: KeywordItem[];
  other_resume_skills: string[];
}

export interface Deduction {
  points_lost: number;
  reason: string;
  evidence: string;
  fix_suggestion: string;
}

export interface DimensionScore {
  key: string;
  name: string;
  points_earned: number;
  max_points: number;
  score_percentage: number;
  status: 'strong' | 'good' | 'needs_improvement';
  summary: string;
  evidence: string[];
  deductions: Deduction[];
  recommendations: string[];
}

export interface ActionItem {
  id: string;
  priority: 'High' | 'Medium' | 'Low';
  category: string;
  title: string;
  explanation: string;
  example_fix?: string | null;
  suggested_revision?: string | null;
}

export interface JobComparison {
  job_title_detected?: string | null;
  seniority_match?: string | null;
  years_experience_required?: number | null;
  years_experience_found?: number | null;
  degree_required?: string | null;
  degree_found?: string | null;
  key_responsibilities_matched: string[];
  key_responsibilities_missing: string[];
}

export interface ATSScorecard {
  overall_score: number;
  tier: 'Strong' | 'Good' | 'Fair' | 'Needs Improvement';
  mode: 'job_matched' | 'resume_only';
  mode_description: string;
  dimension_scores: Record<string, DimensionScore>;
  keyword_analysis: KeywordAnalysis;
  strengths: string[];
  areas_for_improvement: string[];
  prioritized_action_items: ActionItem[];
  ats_formatting_warnings: string[];
  job_comparison?: JobComparison | null;
}

export interface ImprovementSuggestion {
  id: string;
  section: string;
  original_text: string;
  suggested_text: string;
  rationale: string;
  category: string;
  status: 'pending' | 'accepted' | 'rejected';
}
