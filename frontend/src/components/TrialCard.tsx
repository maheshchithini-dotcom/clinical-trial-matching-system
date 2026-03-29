import React from 'react';
import { motion } from 'framer-motion';
import { FlaskConical, ExternalLink, Cpu, ShieldCheck, BadgeInfo } from 'lucide-react';

interface TrialCardProps {
  trial: {
    nct_id: string;
    title?: string;
    condition: string;
    text?: string;
    eligibility?: string;
  };
  match?: {
    score: number;
    confidence: string;
    explanation: string;
  };
  index?: number;
}

const TrialCard: React.FC<TrialCardProps> = ({ trial, match, index = 0 }) => {
  const scorePercent = match ? Math.round(match.score * 100) : null;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`group p-6 bg-white border border-slate-200 rounded-3xl shadow-sm hover:shadow-md transition-all ${match ? 'border-indigo-100' : ''}`}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="space-y-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{trial.nct_id || 'N/A'}</span>
          <h3 className="text-lg font-bold text-slate-900 line-clamp-2 leading-tight group-hover:text-indigo-600 transition-colors">
            {trial.title || 'Clinical Research Study'}
          </h3>
        </div>
        {scorePercent !== null && (
          <div className="flex flex-col items-center p-2 bg-indigo-50 rounded-xl border border-indigo-100 min-w-[64px]">
            <span className="text-lg font-black text-indigo-600 leading-none">{scorePercent}%</span>
            <span className="text-[8px] font-bold text-indigo-400 uppercase mt-1">Match</span>
          </div>
        )}
      </div>

      <div className="space-y-3">
        <div className="flex flex-wrap gap-1">
          {(trial.condition || 'General').split(',').map((c, i) => (
            <span key={i} className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px] font-medium uppercase">
              {c.trim()}
            </span>
          ))}
        </div>
        
        <p className="text-sm text-slate-500 line-clamp-3 leading-relaxed">
          {trial.text || 'No description available for this study.'}
        </p>
      </div>

      {match && (
        <div className="mt-4 pt-4 border-t border-slate-50 space-y-3">
          <div className="flex items-start space-x-3">
            <div className="p-1.5 bg-indigo-50 text-indigo-600 rounded-lg shrink-0">
              <Cpu size={14} />
            </div>
            <div>
               <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">AI Matching Analysis</p>
               <p className="text-sm text-slate-700 font-medium italic leading-relaxed">"{match.explanation}"</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
             <ShieldCheck size={14} className="text-green-500" />
             <span className="text-[10px] font-bold text-slate-500 uppercase">Analysis Confidence: <span className="text-indigo-600">{match.confidence}</span></span>
          </div>
        </div>
      )}

      <div className="mt-6 flex items-center justify-between">
        <div className="flex items-center space-x-1 text-slate-400">
           <FlaskConical size={14} />
           <span className="text-[10px] font-bold uppercase tracking-tight">Active Recruitment</span>
        </div>
        <a 
          href={`https://clinicaltrials.gov/study/${trial.nct_id}`}
          target="_blank"
          rel="noreferrer"
          className="text-xs font-bold text-indigo-600 hover:text-indigo-800 flex items-center space-x-1"
        >
          <span>Source</span>
          <ExternalLink size={12} />
        </a>
      </div>
    </motion.div>
  );
};

export default TrialCard;
