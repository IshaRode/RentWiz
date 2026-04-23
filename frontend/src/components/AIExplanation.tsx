'use client';
import { Sparkles } from 'lucide-react';

interface AIExplanationProps {
  explanation: string;
  isLoading?: boolean;
}

export default function AIExplanation({ explanation, isLoading }: AIExplanationProps) {
  if (isLoading) {
    return (
      <div className="flex items-start gap-3 bg-violet-500/5 border border-violet-500/20 rounded-xl p-4">
        <Sparkles size={16} className="text-violet-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1 space-y-2">
          <div className="skeleton h-3 w-full" />
          <div className="skeleton h-3 w-4/5" />
        </div>
      </div>
    );
  }

  if (!explanation) return null;

  return (
    <div className="flex items-start gap-3 bg-violet-500/5 border border-violet-500/20 rounded-xl p-4">
      <div className="flex-shrink-0 w-7 h-7 rounded-lg bg-violet-500/20 flex items-center justify-center">
        <Sparkles size={13} className="text-violet-400" />
      </div>
      <div>
        <p className="text-xs font-semibold text-violet-400 mb-1">AI Analysis</p>
        <p className="text-sm text-gray-300 leading-relaxed">{explanation}</p>
      </div>
    </div>
  );
}
