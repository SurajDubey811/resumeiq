import React, { useState } from 'react';
import { ParsedResume } from '../types';
import { X, Check, FileText, AlertTriangle, User, Mail, Phone, Globe } from 'lucide-react';

interface ExtractionReviewModalProps {
  parsedResume: ParsedResume;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (updatedText: string) => void;
}

export const ExtractionReviewModal: React.FC<ExtractionReviewModalProps> = ({
  parsedResume,
  isOpen,
  onClose,
  onConfirm,
}) => {
  const [editedText, setEditedText] = useState(parsedResume.raw_text);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                Review Extracted Resume Text
              </h3>
              <p className="text-xs text-slate-400">
                Verify that all sections, dates, and bullets were cleanly extracted before scoring.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Warning if scanned or OCR flagged */}
        {parsedResume.warnings.length > 0 && (
          <div className="mx-6 mt-4 p-3.5 bg-amber-950/30 border border-amber-500/30 rounded-xl flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div className="text-xs text-amber-200">
              <span className="font-semibold block mb-0.5">Extraction Warnings Detected:</span>
              <ul className="list-disc list-inside space-y-0.5 text-amber-300/90">
                {parsedResume.warnings.map((w, idx) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Metadata & Contact Chips */}
        <div className="px-6 py-3 border-b border-slate-800/80 bg-slate-950/40 flex flex-wrap gap-4 text-xs">
          <div className="flex items-center gap-1.5 text-slate-300">
            <User className="w-3.5 h-3.5 text-indigo-400" />
            <span className="font-medium">{parsedResume.filename}</span>
            <span className="text-slate-500 font-mono">({parsedResume.word_count} words)</span>
          </div>

          {parsedResume.contact_info.email && (
            <div className="flex items-center gap-1.5 text-slate-300">
              <Mail className="w-3.5 h-3.5 text-emerald-400" />
              <span>{parsedResume.contact_info.email}</span>
            </div>
          )}

          {parsedResume.contact_info.phone && (
            <div className="flex items-center gap-1.5 text-slate-300">
              <Phone className="w-3.5 h-3.5 text-blue-400" />
              <span>{parsedResume.contact_info.phone}</span>
            </div>
          )}

          {parsedResume.contact_info.linkedin && (
            <div className="flex items-center gap-1.5 text-slate-300">
              <Globe className="w-3.5 h-3.5 text-purple-400" />
              <span>{parsedResume.contact_info.linkedin}</span>
            </div>
          )}
        </div>

        {/* Editable Text Area */}
        <div className="flex-1 p-6 overflow-y-auto">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Editable Document Text (Correct any formatting or character glitches below):
          </label>
          <textarea
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            rows={16}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-200 font-mono text-xs leading-relaxed focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
            placeholder="Parsed resume text appears here..."
          />
        </div>

        {/* Footer Actions */}
        <div className="p-5 border-t border-slate-800 bg-slate-900/90 flex items-center justify-between">
          <button
            onClick={() => setEditedText(parsedResume.raw_text)}
            className="text-xs text-slate-400 hover:text-slate-200 transition"
          >
            Reset to Original Extracted Text
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-medium text-slate-300 hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              onClick={() => onConfirm(editedText)}
              className="px-5 py-2 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
            >
              <Check className="w-4 h-4" />
              <span>Confirm & Analyze</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
