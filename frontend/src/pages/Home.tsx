import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { patientService, trialService } from '../services/api';
import { Activity, Users, Database } from 'lucide-react';
import { motion } from 'framer-motion';

import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  const { data: patients, isError: isPatientsError } = useQuery({
    queryKey: ['patients'],
    queryFn: patientService.getPatients,
  });

  const { data: trials, isError: isTrialsError } = useQuery({
    queryKey: ['trials'],
    queryFn: trialService.getTrials,
  });

  const health = isPatientsError || isTrialsError ? 'fail' : (patients && trials ? 'ok' : 'pending');

  const cards = [
    { title: 'Total Patients', value: patients ? patients.length : 0, icon: Users, color: 'text-blue-500' },
    { title: 'Clinical Trials', value: trials ? trials.length : 0, icon: Database, color: 'text-indigo-500' },
    { title: 'API Status', value: health === 'ok' ? 'Healthy' : health === 'fail' ? 'Down' : 'Checking...', icon: Activity, color: health === 'ok' ? 'text-green-500' : 'text-red-500' },
  ];

  return (
    <div className="space-y-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">
          Clinical Trial Matching <span className="text-indigo-600">Reimagined</span>
        </h1>
        <p className="max-w-2xl mx-auto text-lg text-slate-600">
          Harness the power of AI to match patients with life-saving clinical trials in seconds.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        {cards.map((card, idx) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center space-x-4">
              <div className={`p-3 rounded-xl bg-slate-50 ${card.color}`}>
                <card.icon size={24} />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500">{card.title}</p>
                <h3 className="text-2xl font-bold text-slate-900">{card.value}</h3>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="p-8 bg-indigo-600 rounded-3xl text-white overflow-hidden relative">
        <div className="relative z-10 space-y-4 max-w-lg">
          <h2 className="text-2xl font-bold">Ready to start matching?</h2>
          <p className="text-indigo-100 italic">
            "We focus on accuracy. Our AI scans medical histories to find the perfect study match automatically."
          </p>
          <div className="flex space-x-4 pt-2">
            <button 
              onClick={() => navigate('/patients')}
              className="px-5 py-2.5 bg-white text-indigo-600 font-semibold rounded-xl hover:bg-indigo-50 transition-colors"
            >
              Add a Patient
            </button>
          </div>
        </div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full -mr-20 -mt-20 blur-3xl"></div>
      </div>
    </div>
  );
};

export default Home;
