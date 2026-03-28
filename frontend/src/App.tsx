import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Beaker, Users, ChevronRight, Search, ClipboardList, Database } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import PatientForm from './components/PatientForm';
import TrialCard from './components/TrialCard';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function App() {
  const [loading, setLoading] = useState(false);
  const [matches, setMatches] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [fetchingTrials, setFetchingTrials] = useState(false);

  const handleMatch = async (patientData: any) => {
    setLoading(true);
    setError(null);
    try {
      // 1. Post patient
      const patientResponse = await axios.post(`${API_BASE_URL}/patient`, patientData);
      const patientId = patientResponse.data.patient_id;

      // 2. Get matches
      const matchResponse = await axios.get(`${API_BASE_URL}/match/${patientId}`);
      setMatches(matchResponse.data.matches);
    } catch (err) {
      setError('Failed to fetch matches. Please ensure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchUpdates = async () => {
    setFetchingTrials(true);
    try {
      await axios.post(`${API_BASE_URL}/fetch_trials`, null, { params: { condition: 'Diabetes' } });
      alert('Latest trials fetched from ClinicalTrials.gov!');
    } catch (err) {
      console.error(err);
    } finally {
      setFetchingTrials(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-white font-sans selection:bg-primary/30">
      {/* Navbar */}
      <nav className="border-b border-white/5 bg-background/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-tr from-primary to-accent p-2 rounded-xl shadow-lg shadow-primary/20">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
              ClinicalMatcher <span className="text-primary">AI</span>
            </span>
          </div>
          <button 
            onClick={handleFetchUpdates}
            disabled={fetchingTrials}
            className="flex items-center gap-2 px-4 py-2 rounded-full border border-white/10 hover:bg-white/5 transition-all disabled:opacity-50"
          >
            <Database className={`w-4 h-4 ${fetchingTrials ? 'animate-spin' : ''}`} />
            {fetchingTrials ? 'Syncing...' : 'Sync ClinicalTrials.gov'}
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          {/* Left: Input Form */}
          <div className="lg:col-span-5">
            <div className="sticky top-32">
              <div className="mb-8">
                <h1 className="text-4xl font-bold mb-4">Patient Matching</h1>
                <p className="text-white/50 text-lg leading-relaxed">
                  Enter patient clinical history and conditions to find the most relevant clinical trials using our Hybrid AI match engine.
                </p>
              </div>
              <PatientForm onSubmit={handleMatch} loading={loading} />
            </div>
          </div>

          {/* Right: Results */}
          <div className="lg:col-span-7">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-semibold flex items-center gap-2">
                <ClipboardList className="w-6 h-6 text-primary" />
                Matached Trials
              </h2>
              <span className="text-white/40 text-sm">{matches.length} Results Found</span>
            </div>

            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 mb-8">
                {error}
              </div>
            )}

            <div className="space-y-6">
              <AnimatePresence mode="popLayout">
                {matches.length > 0 ? (
                  matches.map((match, idx) => (
                    <TrialCard key={match.nct_id} match={match} index={idx} />
                  ))
                ) : !loading && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center py-20 border-2 border-dashed border-white/5 rounded-3xl"
                  >
                    <div className="p-4 bg-white/5 rounded-full mb-4">
                      <Search className="w-8 h-8 text-white/20" />
                    </div>
                    <p className="text-white/30 font-medium">No matches to display yet.</p>
                  </motion.div>
                )}
              </AnimatePresence>
              
              {loading && (
                <div className="space-y-6">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-48 bg-white/5 animate-pulse rounded-3xl border border-white/5" />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
