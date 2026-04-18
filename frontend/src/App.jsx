import React, { useState } from 'react';
import { ShieldAlert, User, Database, Microscope } from 'lucide-react';
import UserApp from './userApp';
import AdminApp from './adminApp';
import ResearcherApp from './researcherApp';

export default function App() {
  const [selectedRole, setSelectedRole] = useState(null);

  const handleBack = () => setSelectedRole(null);

  if (selectedRole === 'admin') return <AdminApp onBack={handleBack} />;
  if (selectedRole === 'researcher') return <ResearcherApp onBack={handleBack} />;
  if (selectedRole === 'user') return <UserApp onBack={handleBack} />;

  return (
    <div className="min-h-screen bg-[#050b14] flex flex-col items-center justify-center p-4 text-white">
      <div className="text-center mb-12">
        <ShieldAlert className="text-blue-500 w-16 h-16 mx-auto mb-4" />
        <h1 className="text-4xl font-bold mb-2">TideSense Portal</h1>
        <p className="text-slate-400">Lütfen giriş yapmak istediğiniz yetki tipini seçin</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
        <button onClick={() => setSelectedRole('user')} className="bg-slate-900/50 border border-slate-800 p-8 rounded-3xl text-left hover:border-blue-500 transition-all">
          <User className="w-10 h-10 mb-4 text-blue-500" />
          <h3 className="text-xl font-bold">Kullanıcı</h3>
          <p className="text-sm text-slate-500">Standart izleme araçları</p>
        </button>

        <button onClick={() => setSelectedRole('researcher')} className="bg-slate-900/50 border border-slate-800 p-8 rounded-3xl text-left hover:border-indigo-500 transition-all">
          <Microscope className="w-10 h-10 mb-4 text-indigo-500" />
          <h3 className="text-xl font-bold">Araştırmacı</h3>
          <p className="text-sm text-slate-500">Tarihsel analiz ve grafikler</p>
        </button>

        <button onClick={() => setSelectedRole('admin')} className="bg-slate-900/50 border border-slate-800 p-8 rounded-3xl text-left hover:border-red-500 transition-all">
          <Database className="w-10 h-10 mb-4 text-red-500" />
          <h3 className="text-xl font-bold">Yönetici</h3>
          <p className="text-sm text-slate-500">Sistem ve log ayarları</p>
        </button>
      </div>
    </div>
  );
}
