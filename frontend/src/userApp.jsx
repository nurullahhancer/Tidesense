import React, { useState, useEffect } from 'react';
import { AlertTriangle, Map as MapIcon, Camera, LogOut, ArrowLeft } from 'lucide-react';

export default function UserApp({ onBack }) {
  const [auth, setAuth] = useState({ isLogged: false, name: '' });
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('risk');
  const [readings, setReadings] = useState([]);

  // VERİTABANISIZ GİRİŞ SİMÜLASYONU
  const handleLogin = (e) => {
    e.preventDefault();
    if (username === 'user' && password === '1234') {
      setAuth({ isLogged: true, name: 'Test Kullanıcısı' });
      setError('');
    } else {
      setError('Hatalı giriş. (İpucu: user / 1234)');
    }
  };

  // API YERİNE SAHTE VERİ ÜRETİCİSİ
  useEffect(() => {
    if(auth.isLogged) {
      setReadings([{ water_level: "185.2" }]); // İlk veri
      const timer = setInterval(() => {
        setReadings([{ water_level: (Math.random() * 40 + 160).toFixed(1) }]);
      }, 3000);
      return () => clearInterval(timer);
    }
  }, [auth.isLogged]);

  if (!auth.isLogged) {
    return (
      <div className="min-h-screen bg-[#050b14] flex items-center justify-center p-4">
        <div className="bg-slate-900 p-8 rounded-3xl w-full max-w-md border border-blue-500/30">
          <button onClick={onBack} className="text-slate-500 mb-6 flex items-center gap-2"><ArrowLeft size={16}/> Geri</button>
          <h2 className="text-2xl text-white font-bold mb-6">Kullanıcı Test Girişi</h2>
          <form onSubmit={handleLogin} className="space-y-4">
            <input type="text" placeholder="Kullanıcı Adı (user)" value={username} onChange={e=>setUsername(e.target.value)} className="w-full p-3 bg-slate-800 rounded-xl text-white outline-none" required />
            <input type="password" placeholder="Şifre (1234)" value={password} onChange={e=>setPassword(e.target.value)} className="w-full p-3 bg-slate-800 rounded-xl text-white outline-none" required />
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <button className="w-full bg-blue-600 text-white p-3 rounded-xl font-bold">Giriş Yap</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-[#050b14] text-white">
      <aside className="w-64 border-r border-slate-800 p-6 flex flex-col">
        <h2 className="text-xl font-bold text-blue-500 mb-8">User Portal</h2>
        <nav className="flex-1 space-y-2">
          {[{id:'risk', label:'Risk Durumu', icon:AlertTriangle}, {id:'map', label:'Harita', icon:MapIcon}, {id:'cameras', label:'Kameralar', icon:Camera}].map(item => (
            <button key={item.id} onClick={()=>setActiveTab(item.id)} className={`w-full flex items-center gap-3 p-3 rounded-xl ${activeTab === item.id ? 'bg-blue-600/20 text-blue-400' : 'text-slate-400'}`}>
              <item.icon size={20}/> {item.label}
            </button>
          ))}
        </nav>
        <button onClick={()=>setAuth({isLogged:false})} className="flex items-center gap-2 text-red-400 mt-auto p-2"><LogOut size={20}/> Çıkış</button>
      </aside>
      <main className="flex-1 p-8">
        <h1 className="text-2xl font-bold mb-4">Hoş geldin, {auth.name}</h1>
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl">
           {activeTab === 'risk' && readings.length > 0 ? (
             <div>
               <p className="text-slate-400 mb-2">Canlı Su Seviyesi (Sahte Veri):</p>
               <div className="text-4xl font-bold text-blue-400">{readings[0].water_level} cm</div>
             </div>
           ) : `${activeTab} sayfası içeriği`}
        </div>
      </main>
    </div>
  );
}