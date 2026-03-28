import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Home as HomeIcon, Users, Database, Sparkles, Layout as LayoutIcon, BrainCircuit } from 'lucide-react';
import Home from './pages/Home';
import Patients from './pages/Patients';
import Trials from './pages/Trials';
import Matching from './pages/Matching';

const Navbar = () => {
  const location = useLocation();
  
  const links = [
    { to: '/', label: 'Overview', icon: HomeIcon },
    { to: '/patients', label: 'Patients', icon: Users },
    { to: '/trials', label: 'Clinical Trials', icon: Database },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-40 bg-white/70 backdrop-blur-xl border-b border-slate-200 h-16 flex items-center px-6">
      <div className="max-w-7xl mx-auto w-full flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-2 text-indigo-600">
          <div className="p-1 px-2 border-2 border-indigo-600 rounded-lg">
            <span className="font-extrabold text-xl tracking-tighter">CT</span>
          </div>
          <span className="font-bold text-slate-900 tracking-tight hidden sm:inline-block">Match AI</span>
        </Link>
        
        <div className="flex items-center space-x-1 sm:space-x-4">
          {links.map(link => {
            const Icon = link.icon;
            const isActive = location.pathname === link.to;
            return (
              <Link 
                key={link.to} 
                to={link.to}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all ${
                  isActive 
                    ? 'bg-indigo-50 text-indigo-600 font-bold' 
                    : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <Icon size={18} />
                <span className="hidden sm:inline-block text-sm">{link.label}</span>
              </Link>
            );
          })}
        </div>

        <Link to="/matching" className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-xl shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all text-sm font-semibold">
           <BrainCircuit size={18} />
           <span className="hidden md:inline-block">AI Matcher</span>
        </Link>
      </div>
    </nav>
  );
};

const App = () => {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-indigo-100 selection:text-indigo-900">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-6 pt-24 pb-12 min-h-[calc(100vh-64px)]">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            transition={{ duration: 0.2 }}
          >
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/patients" element={<Patients />} />
              <Route path="/trials" element={<Trials />} />
              <Route path="/matching" element={<Matching />} />
            </Routes>
          </motion.div>
        </AnimatePresence>
      </main>

      <footer className="border-t border-slate-200 bg-white py-8">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row justify-between items-center text-slate-500 text-sm">
          <p>© 2026 Clinical Trial Matching System. All rights reserved.</p>
          <div className="flex space-x-6 mt-4 sm:mt-0">
             <span className="flex items-center space-x-1">
               <div className="w-2 h-2 rounded-full bg-green-500"></div>
               <span>AI Engine: Online</span>
             </span>
             <span>Privacy Policy</span>
             <span>Terms of Service</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
