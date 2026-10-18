import { ParsedResume, ATSScorecard, ImprovementSuggestion, ExtractedSection } from '../types';

const API_BASE = '/api';

export async function parseResume(file: File): Promise<ParsedResume> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/resumes/parse`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to parse resume.' }));
    throw new Error(errorData.detail || `Server returned ${res.status}`);
  }

  const payload = await res.json();
  if (!payload.success || !payload.data) {
    throw new Error(payload.error || 'Failed to parse resume document.');
  }

  return payload.data;
}

export async function analyzeResume(
  resumeText: string,
  jobDescription?: string,
  filename?: string,
  parsedResume?: ParsedResume
): Promise<ATSScorecard> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_text: resumeText,
      job_description: jobDescription || null,
      filename: filename || 'resume.pdf',
      parsed_resume: parsedResume || null,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to analyze resume.' }));
    throw new Error(errorData.detail || `Analysis failed with status ${res.status}`);
  }

  const payload = await res.json();
  if (!payload.success || !payload.scorecard) {
    throw new Error(payload.error || 'Failed to calculate ATS scorecard.');
  }

  return payload.scorecard;
}

export async function improveResume(
  resumeText: string,
  jobDescription?: string,
  sections?: ExtractedSection[],
  useAI: boolean = false
): Promise<{ suggestions: ImprovementSuggestion[]; aiUsed: boolean; disclaimer: string }> {
  const res = await fetch(`${API_BASE}/resumes/improve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_text: resumeText,
      job_description: jobDescription || null,
      sections: sections || null,
      use_ai: useAI,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to get improvement suggestions.' }));
    throw new Error(errorData.detail || `Improvement request failed (${res.status})`);
  }

  const payload = await res.json();
  return {
    suggestions: payload.suggestions || [],
    aiUsed: payload.ai_used || false,
    disclaimer: payload.disclaimer || '',
  };
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
