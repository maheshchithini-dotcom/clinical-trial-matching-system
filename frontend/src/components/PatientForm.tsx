import React, { useState, useRef } from 'react';
import axios from 'axios';
import { User, Calendar, FileText, Send, Upload, FileCheck, AlertCircle } from 'lucide-react';

interface PatientFormProps {
  onSubmit: (data: any) => void;
  loading: boolean;
}

const PatientForm: React.FC<PatientFormProps> = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    age: 45,
    gender: 'male',
    conditions: 'Diabetes, Hypertension',
    history: ''
  });
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      conditions: formData.conditions.split(',').map(c => c.trim())
    });
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formDataFile = new FormData();
    formDataFile.append('file', file);

    setIsUploading(true);
    setUploadError(null);
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/patient/parse_document`, formDataFile);
      setFormData(prev => ({ ...prev, history: response.data.text }));
    } catch (err) {
      setUploadError('Failed to parse document. Please ensure it is a PDF, DOCX, or TXT file.');
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-card border border-white/5 rounded-3xl p-8 shadow-2xl space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-2">
          <label className="text-xs uppercase tracking-widest text-white/40 font-bold ml-1">Age</label>
          <div className="relative">
            <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20" />
            <input 
              type="number" 
              value={formData.age}
              onChange={e => setFormData({...formData, age: parseInt(e.target.value)})}
              className="w-full bg-background border border-white/10 rounded-2xl py-4 pl-12 pr-4 focus:outline-none focus:border-primary transition-all"
              placeholder="e.g. 45"
            />
          </div>
        </div>
        <div className="space-y-2">
          <label className="text-xs uppercase tracking-widest text-white/40 font-bold ml-1">Gender</label>
          <div className="relative">
            <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20" />
            <select 
              value={formData.gender}
              onChange={e => setFormData({...formData, gender: e.target.value})}
              className="w-full bg-background border border-white/10 rounded-2xl py-4 pl-12 pr-4 focus:outline-none focus:border-primary transition-all appearance-none"
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-xs uppercase tracking-widest text-white/40 font-bold ml-1">Conditions</label>
        <input 
          type="text" 
          value={formData.conditions}
          onChange={e => setFormData({...formData, conditions: e.target.value})}
          className="w-full bg-background border border-white/10 rounded-2xl py-4 px-6 focus:outline-none focus:border-primary transition-all"
          placeholder="Comma separated: Diabetes, Lung Cancer..."
        />
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between ml-1">
          <label className="text-xs uppercase tracking-widest text-white/40 font-bold">Clinical History / Report</label>
          <button 
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-primary hover:text-white transition-colors border border-primary/20 bg-primary/5 px-2.5 py-1 rounded-lg"
          >
            {isUploading ? <div className="w-3 h-3 border border-white/30 border-t-white rounded-full animate-spin" /> : <Upload className="w-3 h-3" />}
            {isUploading ? 'Parsing...' : 'Upload Report'}
          </button>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            className="hidden" 
            accept=".pdf,.docx,.txt"
          />
        </div>
        
        <div className="relative">
          <FileText className="absolute left-4 top-6 w-4 h-4 text-white/20" />
          <textarea 
            value={formData.history}
            onChange={e => setFormData({...formData, history: e.target.value})}
            className="w-full bg-background border border-white/10 rounded-2xl py-5 pl-12 pr-6 h-48 focus:outline-none focus:border-primary transition-all resize-none shadow-inner"
            placeholder="Paste detailed clinical history or upload a report above..."
          />
          {formData.history && (
            <div className="absolute right-4 bottom-4 flex items-center gap-1.5 text-[10px] font-bold uppercase text-secondary/60 bg-secondary/5 px-2 py-1 rounded-md border border-secondary/10">
              <FileCheck className="w-3 h-3" /> Report Ready
            </div>
          )}
        </div>
        {uploadError && (
          <div className="flex items-center gap-1.5 text-[10px] text-red-400 font-medium ml-1">
            <AlertCircle className="w-3 h-3" /> {uploadError}
          </div>
        )}
      </div>

      <button 
        type="submit" 
        disabled={loading || isUploading}
        className="w-full bg-gradient-to-r from-primary to-accent hover:shadow-lg hover:shadow-primary/30 transition-all py-5 rounded-2xl font-bold flex items-center justify-center gap-3 disabled:opacity-50"
      >
        {loading ? (
          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        ) : (
          <>
            <Send className="w-5 h-5" />
            Generate Smart Matches
          </>
        )}
      </button>
    </form>
  );
};

export default PatientForm;
