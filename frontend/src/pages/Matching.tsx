import React, { useEffect, useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { matchingService, patientService } from '../services/api';
import TrialCard from '../components/TrialCard';
import { Sparkles, BrainCircuit, ArrowLeft, Trophy, Brain } from 'lucide-react';
import { motion } from 'framer-motion';

const Matching = () => {
  const location = useLocation();
  const patientId = new URLSearchParams(location.search).get('patientId');
  
  const [results, setResults] = useState<any[]>([]);
  const [patient, setPatient] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (patientId) {
      runMatch(parseInt(patientId));
    }
  }, [patientId]);

  const runMatch = async (id: number) => {
    setLoading(true);
    setError('');
    try {
      const [pat, matches] = await Promise.all([
        patientService.getPatients().then(all => all.find((p:any) => p.id === id)),
        matchingService.matchPatient(id)
      ]);
      setPatient(pat);
      setResults(matches);
    } catch (err: any) {
      console.error('Matching failed', err);
      setError('AI clinical analysis failed. The backend might be starting up—please try again after a few seconds.');
    } finally {
      setLoading(false);
    }
  };

  if (!patientId) {
    return (
      <div className="text-center p-20 bg-white rounded-3xl border border-slate-200">
        <Sparkles className="mx-auto text-indigo-200 mb-6" size={64} />
        <h2 className="text-2xl font-bold text-slate-900">Select a patient to start matching</h2>
        <p className="text-slate-500 mb-8 mt-2">We need patient clinical data to run our AI analysis.</p>
        <Link to="/patients" className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-colors">
          Go to Patients
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link to="/patients" className="flex items-center space-x-2 text-slate-500 hover:text-indigo-600 transition-colors">
          <ArrowLeft size={18} />
          <span>Back to Directory</span>
        </Link>
        <div className="flex items-center space-x-2 text-indigo-600 bg-indigo-50 px-3 py-1 rounded-lg text-sm font-bold uppercase tracking-widest">
          <BrainCircuit size={16} />
          <span>AI Engine: Active</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Target Profile</h3>
            {patient ? (
              <div className="space-y-4">
                <div className="pb-4 border-b border-slate-100">
                  <p className="text-xs font-bold text-indigo-600 uppercase mb-1">Patient</p>
                  <p className="text-xl font-bold text-slate-900">{patient.name || 'Anonymous'}</p>
                  <p className="text-sm text-slate-500">{patient.gender}, {patient.age} years old</p>
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase mb-2">Primary Conditions</p>
                  <div className="flex flex-wrap gap-2">
                    {patient.conditions.split(',').map((c: string) => (
                      <span key={c} className="px-2.5 py-1 bg-slate-50 border border-slate-200 text-slate-600 rounded-lg text-xs font-medium">
                        {c.trim()}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                   <p className="text-xs font-bold text-slate-400 uppercase mb-2">Clinical History</p>
                   <p className="text-sm text-slate-600 leading-relaxed italic line-clamp-4">
                     {patient.history}
                   </p>
                </div>
              </div>
            ) : (
              <p className="text-slate-400">Loading profile...</p>
            )}
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center space-x-3 mb-2">
            <h2 className="text-2xl font-bold text-slate-900 font-display">Match Results</h2>
            <div className="px-2 py-0.5 bg-indigo-600 text-white rounded text-[10px] font-bold">TOP 10</div>
          </div>

          {loading ? (
            <div className="space-y-4">
               {[1,2,3].map(i => (
                 <div key={i} className="h-48 bg-slate-100 rounded-3xl animate-pulse"></div>
               ))}
            </div>
          ) : error ? (
            <div className="p-12 text-center bg-red-50 border border-red-100 rounded-3xl">
              <p className="text-red-700 font-medium">{error}</p>
              <button 
                onClick={() => runMatch(parseInt(patientId))}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded-xl text-sm"
              >
                Retry Analysis
              </button>
            </div>
          ) : results.length === 0 ? (
            <div className="p-20 text-center text-slate-400">No matches found for this profile.</div>
          ) : (
            <div className="space-y-4">
              {results.map((result, idx) => (
                <motion.div
                  key={result.trial_id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <TrialCard 
                    trial={result} 
                    match={{
                      score: result.score,
                      confidence: result.confidence,
                      explanation: result.explanation
                    }} 
                    index={idx} 
                  />
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Matching;
