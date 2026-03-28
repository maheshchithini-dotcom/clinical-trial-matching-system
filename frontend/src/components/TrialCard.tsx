import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, FlaskConical, ExternalLink, Cpu, ShieldCheck } from 'lucide-react';

interface TrialCardProps {
  match: {
    nct_id: string;
    title: string;
    condition: string;
    score: number;
    confidence: string;
    explanation: string;
    eligible: boolean;
  };
  index: number;
}

const TrialCard: React.FC<TrialCardProps> = ({ match, index }) => {
  const scorePercent = Math.round(match.score * 100);
  
  const confidenceColors = {
    High: 'text-secondary border-secondary/20 bg-secondary/10',
    Medium: 'text-primary border-primary/20 bg-primary/10',
    Low: 'text-white/40 border-white/10 bg-white/5'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="group bg-card border border-white/5 rounded-3xl p-6 hover:border-primary/30 transition-all hover:bg-white/[0.02] shadow-xl"
    >
      <div className="flex items-start justify-between mb-2">
        <div className="space-y-1 pr-4">
          <div className="flex items-center gap-2 mb-2">
             <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-[10px] font-bold tracking-widest uppercase text-white/40">
                {match.nct_id}
             </span>
             <span className={`px-3 py-1 border rounded-full text-[10px] font-bold tracking-widest uppercase flex items-center gap-1 ${confidenceColors[match.confidence as keyof typeof confidenceColors]}`}>
                <ShieldCheck className="w-3 h-3" /> {match.confidence} Confidence
             </span>
          </div>
          <h3 className="text-xl font-bold leading-tight group-hover:text-primary transition-colors mb-1">
            {match.title || match.condition}
          </h3>
          <p className="text-sm text-white/40 font-medium italic">{match.condition}</p>
        </div>
        
        <div className="flex flex-col items-end shrink-0">
          <div className="text-4xl font-black text-primary drop-shadow-[0_0_10px_rgba(59,130,246,0.3)]">{scorePercent}%</div>
          <div className="text-[10px] font-bold uppercase tracking-widest text-white/30">Match Score</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-2 w-full bg-white/5 rounded-full mb-6 overflow-hidden">
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${scorePercent}%` }}
          className="h-full bg-gradient-to-r from-primary to-accent"
        />
      </div>

      <div className="bg-white/5 rounded-2xl p-5 border border-white/5 mb-6 relative overflow-hidden group/expl">
        <div className="absolute top-0 left-0 w-1 h-full bg-primary/50" />
        <div className="flex items-start gap-4">
          <div className="p-2.5 bg-primary/10 rounded-xl mt-0.5 shadow-inner">
            <Cpu className="w-5 h-5 text-primary" />
          </div>
          <p className="text-[15px] leading-relaxed text-white/80 font-medium">
            {match.explanation}
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between border-t border-white/5 pt-4">
        <div className="flex items-center gap-3 text-white/40">
           <div className="flex items-center gap-1.5 text-xs font-semibold">
              <FlaskConical className="w-4 h-4 text-accent" />
              BioBERT Domain Understanding Active
           </div>
        </div>
        <a 
          href={`https://clinicaltrials.gov/study/${match.nct_id}`}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2 text-primary hover:text-white transition-all text-sm font-bold bg-white/5 px-4 py-2 rounded-xl border border-white/10 hover:bg-primary/20"
        >
          Study Details <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </motion.div>
  );
};

export default TrialCard;
