import React, { useState, useRef } from 'react';
import { patientService } from '../services/api';
import { User, Calendar, Send, Upload, FileCheck, AlertCircle } from 'lucide-react';

interface PatientFormProps {
  onSuccess: () => void;
}

const PatientForm: React.FC<PatientFormProps> = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    age: 45,
    gender: 'male',
    conditions: 'Diabetes, Hypertension',
    history: ''
  });
  const [loading, setLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await patientService.createPatient({
        ...formData,
        conditions: formData.conditions
      });
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save patient.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);
    try {
      const data = await patientService.parseDocument(file);
      setFormData(prev => ({ ...prev, history: data.text }));
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to parse document.';
      setError(`Parsing Error: ${msg}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider ml-1">Age</label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-300" />
            <input 
              type="number" 
              value={formData.age}
              onChange={e => setFormData({...formData, age: parseInt(e.target.value)})}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 pl-10 pr-4 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-all"
            />
          </div>
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider ml-1">Gender</label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-300" />
            <select 
              value={formData.gender}
              onChange={e => setFormData({...formData, gender: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 pl-10 pr-4 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-all appearance-none"
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
      </div>

      <div className="space-y-1.5">
        <label className="text-xs font-bold text-slate-400 uppercase tracking-wider ml-1">Conditions</label>
        <input 
          type="text" 
          value={formData.conditions}
          onChange={e => setFormData({...formData, conditions: e.target.value})}
          className="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 px-4 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-all"
          placeholder="e.g. Diabetes, Hypertension"
        />
      </div>

      <div className="space-y-1.5">
        <div className="flex items-center justify-between ml-1">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Clinical History</label>
          <button 
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="text-[10px] font-bold uppercase text-indigo-600 hover:text-indigo-800 flex items-center gap-1 bg-indigo-50 px-2 py-1 rounded"
          >
            <Upload size={12} />
            {isUploading ? 'Parsing...' : 'Upload Report'}
          </button>
          <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".pdf,.docx,.txt" />
        </div>
        
        <div className="relative">
          <textarea 
            value={formData.history}
            onChange={e => setFormData({...formData, history: e.target.value})}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl py-4 px-4 h-32 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-all resize-none"
            placeholder="Paste clinical history or upload a report..."
          />
          {formData.history && (
            <div className="absolute right-3 bottom-3 flex items-center gap-1 text-[10px] font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded border border-green-100">
              <FileCheck size={12} /> REPORT ATTACHED
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-100 rounded-xl text-red-600 text-xs flex items-center gap-2">
          <AlertCircle size={14} /> 
          <span className="flex-1">
            {typeof error === 'string' ? error : (error as any).message || 'An unexpected error occurred.'}
          </span>
        </div>
      )}

      <button 
        type="submit" 
        disabled={loading || isUploading}
        className="w-full bg-indigo-600 text-white font-bold py-4 rounded-xl hover:bg-indigo-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-100"
      >
        {loading ? <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : (
          <><Send size={18} /><span>Add Patient Record</span></>
        )}
      </button>
    </form>
  );
};

export default PatientForm;
