import React, { useState } from 'react';
import { AlertTriangle, Map as MapIcon, Camera, Activity, Moon, Settings, LogOut, ArrowLeft } from 'lucide-react';

export default function AdminApp({ onBack }) {
  const [auth, setAuth] = useState({ isLogged: false, name: '' });
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('settings');

  // VERİTABANISIZ GİRİŞ SİMÜLASYONU
  const handleLogin = (e) => {
    e.preventDefault();
    if (username === 'admin' && password === '1234') {
      setAuth({ isLogged: true, name: 'Sistem Yöneticisi' });
      setError('');
    } else {
      setError('Hatalı giriş. (İpucu: admin / 1234)');
    }
  };

  if (!auth.isLogged) {
    return (
      <div className="min-h-screen bg-[#050b14] flex items-center justify-center p-4">
        <div className="bg-slate-900 p-8 rounded-3xl w-full max-w-md border border-red-500/30">
          <button onClick={onBack} className="text-slate-500 mb-6 flex items-center gap-2"><ArrowLeft size={16}/> Geri</button>
          <h2 className="text-2xl text-white font-bold mb-6">Yönetici Test Girişi</h2>
          <form onSubmit={handleLogin} className="space-y-4">
            <input type="text" placeholder="Kullanıcı Adı (admin)" value={username} onChange={e=>setUsername(e.target.value)} className="w-full p-3 bg-slate-800 rounded-xl text-white outline-none focus:border-red-500 border border-slate-700" required />
            <input type="password" placeholder="Şifre (1234)" value={password} onChange={e=>setPassword(e.target.value)} className="w-full p-3 bg-slate-800 rounded-xl text-white outline-none focus:border-red-500 border border-slate-700" required />
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <button className="w-full bg-red-600 text-white p-3 rounded-xl font-bold hover:bg-red-500">Sistemi Aç</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-[#020617] text-white">
      <aside className="w-64 border-r border-red-500/20 p-6 flex flex-col bg-slate-950">
        <h2 className="text-xl font-bold text-red-500 mb-8 tracking-widest">ADMIN CORE</h2>
        <nav className="flex-1 space-y-2">
          {[{id:'risk', label:'Risk Durumu', icon:AlertTriangle}, {id:'map', label:'Harita', icon:MapIcon}, {id:'cameras', label:'Kameralar', icon:Camera}, {id:'history', label:'Tarihsel Analiz', icon:Activity}, {id:'moon', label:'Ay Durumu', icon:Moon}, {id:'settings', label:'Sistem Ayarları', icon:Settings}].map(item => (
            <button key={item.id} onClick={()=>setActiveTab(item.id)} className={`w-full flex items-center gap-3 p-3 rounded-xl ${activeTab === item.id ? 'bg-red-600/20 text-red-400' : 'text-slate-400'}`}>
              <item.icon size={20}/> {item.label}
            </button>
          ))}
        </nav>
        <button onClick={()=>setAuth({isLogged:false})} className="flex items-center gap-2 text-slate-500 mt-auto p-2 hover:text-red-400"><LogOut size={20}/> Kapat</button>
      </aside>
      <main className="flex-1 p-8">
        <h1 className="text-2xl font-bold mb-4">Hoş geldin, {auth.name}</h1>
        <div className="bg-red-500/5 border border-red-500/20 p-8 rounded-2xl">
          {activeTab === 'settings' ? 'Eşik Kontrolleri (Admin Test)' : `${activeTab} sayfası`}
        </div>
      </main>
    </div>
  );
}