import React, { useState } from 'react';
import { 
  Microscope, 
  Activity, 
  Moon, 
  LogOut, 
  ArrowLeft, 
  AlertTriangle, 
  Map as MapIcon, 
  Camera,
  Download // İndirme ikonu için eklendi
} from 'lucide-react';
import TideChart from './TideChart'; 

export default function ResearcherApp({ onBack }) {
  const [auth, setAuth] = useState({ isLogged: false, name: '' });
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('history');

  // CSV İNDİRME FONKSİYONU
  const downloadCSV = () => {
    // Örnek Veri Seti (Grafikteki verilerle uyumlu)
    const data = [
      { zaman: "-12s", seviye: 165, tip: "Gerçek" },
      { zaman: "-10s", seviye: 172, tip: "Gerçek" },
      { zaman: "-8s", seviye: 190, tip: "Gerçek" },
      { zaman: "-6s", seviye: 210, tip: "Gerçek" },
      { zaman: "-4s", seviye: 205, tip: "Gerçek" },
      { zaman: "-2s", seviye: 185, tip: "Gerçek" },
      { zaman: "ŞU AN", seviye: 170, tip: "Kesişim" },
      { zaman: "+2s", seviye: 155, tip: "ML Tahmin" },
      { zaman: "+4s", seviye: 140, tip: "ML Tahmin" },
      { zaman: "+6s", seviye: 150, tip: "ML Tahmin" },
      { zaman: "+8s", seviye: 180, tip: "ML Tahmin" },
      { zaman: "+10s", seviye: 205, tip: "ML Tahmin" },
      { zaman: "+12s", seviye: 215, tip: "ML Tahmin" },
    ];

    // CSV Başlıklarını oluştur
    const headers = ["Zaman", "Su Seviyesi (cm)", "Veri Tipi"];
    
    // Satırları oluştur (Virgülle ayırarak)
    const csvRows = [
      headers.join(","), // Başlık satırı
      ...data.map(row => `${row.zaman},${row.seviye},${row.tip}`) // Veri satırları
    ];

    // CSV içeriğini birleştir
    const csvContent = csvRows.join("\n");

    // İndirme dosyasını oluştur (Blob)
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    // Görünmez bir link oluştur ve tıkla (İndirmeyi tetikler)
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `tidesense_rapor_${new Date().toLocaleDateString()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleLogin = (e) => {
    e.preventDefault();
    if (username === 'researcher' && password === '1234') {
      setAuth({ isLogged: true, name: 'Araştırmacı Test' });
      setError('');
    } else {
      setError('Hatalı giriş. (İpucu: researcher / 1234)');
    }
  };

  if (!auth.isLogged) {
    return (
      <div className="min-h-screen bg-[#050b14] flex items-center justify-center p-4">
        <div className="bg-slate-900 p-8 rounded-3xl w-full max-w-md border border-indigo-500/30">
          <button onClick={onBack} className="text-slate-500 mb-6 flex items-center gap-2"><ArrowLeft size={16}/> Geri</button>
          <h2 className="text-2xl text-white font-bold mb-6">Araştırmacı Girişi</h2>
          <form onSubmit={handleLogin} className="space-y-4">
            <input type="text" placeholder="Kullanıcı Adı" value={username} onChange={e=>setUsername(e.target.value)} className="w-full p-3 bg-slate-800 rounded-xl text-white outline-none" required />
            <input type="password" placeholder="Şifre" value={password} onChange={e=>setPassword(e.target.value)} className="w-full p-3 bg-slate-800 rounded-xl text-white outline-none" required />
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <button className="w-full bg-indigo-600 text-white p-3 rounded-xl font-bold">Giriş Yap</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-[#050b14] text-white">
      <aside className="w-64 border-r border-slate-800 p-6 flex flex-col">
        <h2 className="text-xl font-bold text-indigo-400 mb-8 italic">TideSense</h2>
        <nav className="flex-1 space-y-2">
          {[{id:'history', label:'Tarihsel Analiz', icon:Activity}, {id:'risk', label:'Risk Durumu', icon:AlertTriangle}, {id:'map', label:'Harita', icon:MapIcon}, {id:'cameras', label:'Kameralar', icon:Camera}, {id:'moon', label:'Ay Durumu', icon:Moon}].map(item => (
            <button key={item.id} onClick={()=>setActiveTab(item.id)} className={`w-full flex items-center gap-3 p-3 rounded-xl ${activeTab === item.id ? 'bg-indigo-600/20 text-indigo-400' : 'text-slate-400'}`}>
              <item.icon size={20}/> {item.label}
            </button>
          ))}
        </nav>
        <button onClick={()=>setAuth({isLogged:false})} className="flex items-center gap-2 text-red-400 mt-auto p-2"><LogOut size={20}/> Çıkış</button>
      </aside>
      
      <main className="flex-1 p-8 overflow-y-auto">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-2xl font-bold mb-2">Hoş geldin Dr. {auth.name}</h1>
            <p className="text-slate-500">Gelişmiş Veri Analiz Merkezi</p>
          </div>

          {/* CSV İNDİRME BUTONU (GÖREV 3) */}
          <button 
            onClick={downloadCSV}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-indigo-400 border border-indigo-500/30 px-4 py-2 rounded-xl transition-all font-medium"
          >
            <Download size={18} /> Verileri CSV Olarak İndir
          </button>
        </div>
        
        {activeTab === 'history' ? (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-indigo-300">
                <Activity size={20} /> Gelgit Analiz Grafiği
              </h3>
              <div className="h-[400px]">
                <TideChart />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
               <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                 <p className="text-slate-400 text-sm">ML Güven Oranı</p>
                 <p className="text-2xl font-bold text-green-400 mt-1">%94.2</p>
               </div>
               <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl text-center">
                 <p className="text-xs text-slate-500">CSV dışa aktarım özelliği aktif.</p>
               </div>
            </div>
          </div>
        ) : (
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl">
            {activeTab} paneli içeriği test ediliyor...
          </div>
        )}
      </main>
    </div>
  );
}