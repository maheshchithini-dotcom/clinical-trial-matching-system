import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { patientService } from '../services/api';
import PatientForm from '../components/PatientForm';
import { UserPlus, Search, MoreVertical, FileText, XCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';

const Patients = () => {
  const [showForm, setShowForm] = useState(false);
  const queryClient = useQueryClient();

  const { data: patients = [], isLoading: loading } = useQuery({
    queryKey: ['patients'],
    queryFn: patientService.getPatients,
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Patient Directory</h1>
          <p className="text-slate-500">Manage patients and their clinical records.</p>
        </div>
        <button 
          onClick={() => setShowForm(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors"
        >
          <UserPlus size={18} />
          <span>New Patient</span>
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-12 text-center text-slate-400">Loading patients...</div>
        ) : patients.length === 0 ? (
          <div className="p-12 text-center text-slate-400">No patients found. Click "New Patient" to get started.</div>
        ) : (
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider uppercase">Name</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider uppercase">Conditions</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider uppercase">Matches</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {patients.map((p: any) => (
                <tr key={p.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-semibold text-slate-900">{p.name || 'Anonymous User'}</div>
                    <div className="text-xs text-slate-500">{p.gender}, {p.age} years</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {p.conditions.split(',').map((c: string) => (
                        <span key={c} className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded-md text-[10px] uppercase font-bold tracking-tight">
                          {c.trim()}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link 
                      to={`/matching?patientId=${p.id}`}
                      className="inline-flex items-center space-x-1 text-indigo-600 hover:text-indigo-800 font-medium"
                    >
                      <Search size={14} />
                      <span>Run Match</span>
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <button className="text-slate-400 hover:text-slate-600">
                      <MoreVertical size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <AnimatePresence>
        {showForm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden"
            >
              <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                    <FileText size={20} />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-slate-900">Patient Profiling</h2>
                    <p className="text-sm text-slate-500">Auto-parse or manually input clinical data.</p>
                  </div>
                </div>
                <button 
                  onClick={() => setShowForm(false)}
                  className="p-2 hover:bg-slate-100 rounded-full text-slate-400 transition-colors"
                >
                  <XCircle size={24} />
                </button>
              </div>
              <div className="p-6 max-h-[80vh] overflow-y-auto">
                <PatientForm onSuccess={() => { setShowForm(false); queryClient.invalidateQueries({ queryKey: ['patients'] }); }} />
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Patients;
