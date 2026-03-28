import React, { useEffect, useState } from 'react';
import { trialService } from '../services/api';
import TrialCard from '../components/TrialCard';
import { RefreshCw, Search, Database } from 'lucide-react';
import { motion } from 'framer-motion';

const Trials = () => {
  const [trials, setTrials] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState('');

  const fetchTrials = async () => {
    setLoading(true);
    try {
      const data = await trialService.getTrials();
      setTrials(data);
    } catch (error) {
      console.error('Failed to fetch trials', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrials();
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await trialService.syncTrials();
      await fetchTrials();
    } catch (error) {
      console.error('Sync failed', error);
    } finally {
      setSyncing(false);
    }
  };

  const filteredTrials = trials.filter(t => 
    t.title?.toLowerCase().includes(search.toLowerCase()) || 
    t.condition?.toLowerCase().includes(search.toLowerCase()) ||
    t.nct_id?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Available Trials</h1>
          <p className="text-slate-500">Live clinical studies from ClinicalTrials.gov API.</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Search trials..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 pr-4 py-2 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none w-64 text-sm"
            />
          </div>
          <button 
            onClick={handleSync}
            disabled={syncing}
            className={`flex items-center space-x-2 px-4 py-2 ${syncing ? 'bg-slate-100 text-slate-400' : 'bg-white text-indigo-600 border border-slate-200 hover:bg-slate-50'} rounded-xl transition-all shadow-sm`}
          >
            <RefreshCw size={18} className={syncing ? 'animate-spin' : ''} />
            <span>{syncing ? 'Syncing...' : 'Sync Now'}</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} className="h-64 bg-slate-100 rounded-2xl animate-pulse"></div>
          ))}
        </div>
      ) : filteredTrials.length === 0 ? (
        <div className="p-20 text-center bg-white border border-slate-200 rounded-3xl">
          <Database className="mx-auto text-slate-200 mb-4" size={64} />
          <h3 className="text-lg font-semibold text-slate-900">No trials found</h3>
          <p className="text-slate-500">Try syncing with the API or adjusting your search.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTrials.map((trial, idx) => (
            <motion.div
              key={trial.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.05 }}
            >
              <TrialCard trial={trial} />
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Trials;
