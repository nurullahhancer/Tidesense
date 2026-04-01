import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShieldAlert, 
  Wind, 
  Thermometer, 
  Moon, 
  Map as MapIcon, 
  Camera, 
  LogOut,
  User,
  Lock,
  Activity,
  AlertTriangle,
  Compass,
  Navigation,
  ChevronDown,
  Menu,
  X,
  Info
} from 'lucide-react';

// ==========================================
// RASTGELE VERİ ÜRETİCİSİ
// ==========================================
const generateRandomLocations = () => {
  const baseLocations = [
    { id: 1, name: 'İskenderun Limanı', latStr: '36.58° N', lngStr: '36.16° E', lat: 36.58, lng: 36.16 },
    { id: 2, name: 'İzmir Alsancak', latStr: '38.42° N', lngStr: '27.14° E', lat: 38.42, lng: 27.14 },
    { id: 3, name: 'İstanbul Boğazı', latStr: '41.02° N', lngStr: '29.00° E', lat: 41.02, lng: 29.00 },
    { id: 4, name: 'Trabzon Limanı', latStr: '41.00° N', lngStr: '39.71° E', lat: 41.00, lng: 39.71 }
  ];

  return baseLocations.map(loc => {
    const initialWaterLevel = Math.floor(Math.random() * 70) + 90; 
    const moonAltitude = (Math.random() * 30 + 20).toFixed(1); 
    const moonAzimuth = (Math.random() * 180 + 90).toFixed(1); 
    const moonTilt = Math.floor(Math.random() * 40 - 20); 

    return {
      ...loc,
      pressure: Number((Math.random() * 25 + 1000).toFixed(1)), 
      temp: Number((Math.random() * 15 + 15).toFixed(1)), 
      waterLevel: initialWaterLevel,
      status: initialWaterLevel > 150 ? 'Kritik' : 'Normal',
      moonData: { altitude: moonAltitude, azimuth: moonAzimuth, tilt: moonTilt }
    };
  });
};

export default function App() {
  const [auth, setAuth] = useState({ isLoggedIn: false, role: null, username: '' });

  const handleLogin = (username, password, role) => {
    setAuth({ isLoggedIn: true, role: role, username: username });
  };

  const handleLogout = () => {
    setAuth({ isLoggedIn: false, role: null, username: '' });
  };

  return (
    <div className="min-h-screen bg-[#050b14] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-[#050b14] to-black text-slate-200 font-sans selection:bg-blue-500/30 overflow-hidden">
      <AnimatePresence mode="wait">
        {!auth.isLoggedIn ? (
          <LoginScreen key="login" onLogin={handleLogin} />
        ) : (
          <Dashboard key="dashboard" auth={auth} onLogout={handleLogout} />
        )}
      </AnimatePresence>
    </div>
  );
}

// ==========================================
// 1. GİRİŞ EKRANI (LOGIN)
// ==========================================
function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('user');
  const [error, setError] = useState('');

  const submitForm = (e) => {
    e.preventDefault();
    setError('');

    let isValid = false;

    if (role === 'user' && password === '1234') {
      isValid = true;
    } else if (role === 'researcher' && password === '5678') {
      isValid = true;
    } else if (role === 'admin' && password === '0258') {
      isValid = true;
    }

    if (isValid) {
      onLogin(username, password, role);
    } else {
      setError('Hatalı şifre! Lütfen seçtiğiniz role uygun şifreyi giriniz.');
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.96, y: 14 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.96, y: -14 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="min-h-screen flex items-center justify-center p-4 relative"
    >
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[100px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[100px] pointer-events-none"></div>

      <div className="bg-slate-950/70 backdrop-blur-xl border border-white/10 shadow-2xl rounded-[32px] w-full max-w-md overflow-hidden relative z-10">
        <div className="bg-blue-600/20 p-8 text-center border-b border-white/5">
          <Moon className="w-14 h-14 text-blue-400 mx-auto mb-3 drop-shadow-[0_0_15px_rgba(96,165,250,0.5)]" />
          <h1 className="text-3xl font-bold text-white tracking-wider">TideSense</h1>
          <p className="text-blue-200/80 text-sm mt-2">Akıllı Gelgit İzleme Sistemi</p>
        </div>
        
        <form onSubmit={submitForm} className="p-8 space-y-6">
          
          <AnimatePresence>
            {error && (
              <motion.div 
                initial={{ opacity: 0, y: -10, height: 0 }}
                animate={{ opacity: 1, y: 0, height: 'auto' }}
                exit={{ opacity: 0, y: -10, height: 0 }}
                className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm px-4 py-3 rounded-xl flex items-center gap-2"
              >
                <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                <p>{error}</p>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
              <User className="w-4 h-4 text-blue-400" /> Kullanıcı Adı
            </label>
            <input 
              type="text" 
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-white placeholder-slate-500 transition-all"
              placeholder="" 
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Sistem Rolü</label>
            <select 
              value={role} 
              onChange={(e) => setRole(e.target.value)}
              className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-white appearance-none cursor-pointer"
            >
              <option value="user" className="bg-slate-900">Standart Kullanıcı (User)</option>
              <option value="researcher" className="bg-slate-900">Araştırmacı (Researcher)</option>
              <option value="admin" className="bg-slate-900">Sistem Yöneticisi (Admin)</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
              <Lock className="w-4 h-4 text-blue-400" /> Şifre
            </label>
            <input 
              type="password" 
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-white placeholder-slate-500 transition-all"
              placeholder="Role uygun şifreyi giriniz"
            />
          </div>

          <button 
            type="submit" 
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-3.5 rounded-xl shadow-[0_0_20px_rgba(37,99,235,0.3)] transition-all hover:scale-[1.02] active:scale-95 mt-4"
          >
            Sisteme Giriş Yap
          </button>

          <div className="mt-6 pt-4 border-t border-white/5 text-center">
            <p className="text-xs text-slate-400 flex justify-center items-center gap-1.5 mb-2">
              <Info className="w-3.5 h-3.5" /> Test için tanımlı şifreler:
            </p>
            <div className="flex justify-center gap-3 text-[10px] text-slate-500 font-mono">
              <span className="bg-slate-900/50 px-2 py-1 rounded border border-white/5">User: 1234</span>
              <span className="bg-slate-900/50 px-2 py-1 rounded border border-white/5">Rsrc: 5678</span>
              <span className="bg-slate-900/50 px-2 py-1 rounded border border-white/5">Admin: 0258</span>
            </div>
          </div>
        </form>
      </div>
    </motion.div>
  );
}

// ==========================================
// 2. ANA PANEL (DASHBOARD)
// ==========================================
function Dashboard({ auth, onLogout }) {
  const [activeTab, setActiveTab] = useState('risk');
  const [expandedMenu, setExpandedMenu] = useState(null); 
  const [activeLocationId, setActiveLocationId] = useState(null); 
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false); 
  
  const [locations, setLocations] = useState(() => generateRandomLocations());

  useEffect(() => {
    const timer = setInterval(() => {
      setLocations(prev => prev.map(loc => {
        const newWaterLevel = loc.waterLevel + (Math.random() * 2 - 1); 
        return {
          ...loc,
          pressure: Number((loc.pressure + (Math.random() * 0.4 - 0.2)).toFixed(1)),
          temp: Number((loc.temp + (Math.random() * 0.2 - 0.1)).toFixed(1)),
          waterLevel: Number(newWaterLevel.toFixed(1)),
          status: newWaterLevel > 150 ? 'Kritik' : 'Normal'
        };
      }));
    }, 2500);
    return () => clearInterval(timer);
  }, []);

  const menuItems = [
    { id: 'risk', label: 'Risk Durumu', icon: ShieldAlert, hasSubmenu: false },
    { id: 'pressure', label: 'Basınç Değeri', icon: Wind, hasSubmenu: false },
    { id: 'temperature', label: 'Sıcaklık', icon: Thermometer, hasSubmenu: false },
    { id: 'camera', label: 'Kameralar', icon: Camera, hasSubmenu: true },
    { id: 'moon', label: 'Ay Durumu', icon: Moon, hasSubmenu: false },
    { id: 'map', label: 'Harita (Canlı)', icon: MapIcon, hasSubmenu: false },
  ];

  const handleMenuClick = (item) => {
    setActiveTab(item.id);
    if (item.hasSubmenu) {
      const isCurrentlyExpanded = expandedMenu === item.id;
      setExpandedMenu(isCurrentlyExpanded ? null : item.id);
      if (!isCurrentlyExpanded) setActiveLocationId(null); 
    } else {
      setExpandedMenu(null);
      setActiveLocationId(null);
      setIsMobileMenuOpen(false); 
    }
  };

  const handleSubItemClick = (e, locId) => {
    e.stopPropagation();
    setActiveLocationId(locId);
    setIsMobileMenuOpen(false); 
  };

  const SidebarContent = () => (
    <>
      <div className="p-6 text-center border-b border-white/5 relative z-10 flex justify-between items-center md:block">
        <h2 className="text-xl md:text-2xl font-bold text-white flex items-center justify-center gap-3 tracking-wide">
          <Moon className="w-6 h-6 md:w-7 md:h-7 text-blue-400 drop-shadow-[0_0_10px_rgba(96,165,250,0.8)]" /> 
          TideSense
        </h2>
        <button onClick={() => setIsMobileMenuOpen(false)} className="md:hidden p-2 text-slate-400 hover:text-white">
          <X className="w-6 h-6" />
        </button>
        <p className="hidden md:block text-xs text-blue-300/60 mt-2 font-medium tracking-wider">v1.6.1 • SECURE</p>
      </div>
      
      <div className="flex-1 py-4 overflow-y-auto px-4 relative z-10 custom-scrollbar">
        <nav className="space-y-1">
          {menuItems.map(item => {
            const isActive = activeTab === item.id;
            const isExpanded = expandedMenu === item.id;

            return (
              <div key={item.id}>
                <button
                  onClick={() => handleMenuClick(item)}
                  className={`w-full flex items-center justify-between px-4 md:px-5 py-3.5 rounded-2xl transition-all duration-300 relative overflow-hidden group ${
                    isActive ? 'text-white' : 'text-slate-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  {isActive && (
                    <motion.div 
                      layoutId="activeTabBg" 
                      className="absolute inset-0 bg-gradient-to-r from-blue-600/40 to-indigo-600/40 border border-blue-500/30 rounded-2xl md:block hidden"
                    />
                  )}
                  {isActive && (
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-600/40 to-indigo-600/40 border border-blue-500/30 rounded-2xl md:hidden block" />
                  )}
                  
                  <div className="flex items-center gap-4 relative z-10">
                    <item.icon className={`w-5 h-5 transition-transform duration-300 ${isActive ? 'scale-110 drop-shadow-[0_0_8px_rgba(255,255,255,0.5)]' : 'group-hover:scale-110'}`} />
                    <span className="font-semibold tracking-wide text-sm md:text-base">{item.label}</span>
                  </div>

                  {item.hasSubmenu && (
                    <ChevronDown className={`w-4 h-4 relative z-10 transition-transform duration-300 ${isExpanded ? 'rotate-180 text-blue-400' : 'text-slate-500'}`} />
                  )}
                </button>

                <AnimatePresence>
                  {item.hasSubmenu && isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                      className="overflow-hidden"
                    >
                      <div className="pl-12 pr-2 py-2 space-y-1 my-1 border-l border-white/10 ml-6 md:ml-7">
                        <button
                          onClick={(e) => handleSubItemClick(e, null)}
                          className={`w-full text-left px-4 py-2 rounded-xl text-xs md:text-sm font-medium transition-all ${
                            activeLocationId === null 
                              ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' 
                              : 'text-slate-500 hover:text-white hover:bg-white/5'
                          }`}
                        >
                          Tüm Kameralar
                        </button>
                        {locations.map(loc => (
                          <button
                            key={loc.id}
                            onClick={(e) => handleSubItemClick(e, loc.id)}
                            className={`w-full text-left px-4 py-2 rounded-xl text-xs md:text-sm transition-all ${
                              activeLocationId === loc.id 
                                ? 'bg-blue-500/20 text-blue-300 font-bold border border-blue-500/30 shadow-[0_0_10px_rgba(59,130,246,0.1)]' 
                                : 'text-slate-500 hover:text-white hover:bg-white/5'
                            }`}
                          >
                            {loc.name.split(' ')[0]} {loc.name.split(' ')[1]}
                          </button>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </nav>
      </div>

      <div className="p-4 md:p-6 border-t border-white/5 bg-slate-900/30 relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-500 flex items-center justify-center font-bold text-white shadow-lg border border-white/20">
              {auth.username ? auth.username.charAt(0).toUpperCase() : 'U'}
            </div>
            <div>
              <p className="text-sm font-bold text-white">{auth.username || 'Kullanıcı'}</p>
              <p className="text-xs text-blue-400 capitalize">{auth.role}</p>
            </div>
          </div>
          <button onClick={onLogout} className="text-slate-500 hover:text-red-400 transition-colors bg-white/5 p-2 rounded-xl hover:bg-red-500/10" title="Çıkış Yap">
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </>
  );

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col md:flex-row h-screen p-2 md:p-6 gap-4 md:gap-6 relative"
    >
      <div className="absolute top-0 left-1/4 w-[300px] h-[300px] md:w-[500px] md:h-[500px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="md:hidden flex items-center justify-between bg-slate-950/80 backdrop-blur-xl border border-white/10 rounded-2xl px-4 py-3 shadow-lg z-30">
        <div className="flex items-center gap-2">
          <Moon className="w-6 h-6 text-blue-400" />
          <h1 className="font-bold text-white tracking-wide">TideSense</h1>
        </div>
        <button onClick={() => setIsMobileMenuOpen(true)} className="p-2 bg-white/5 rounded-lg text-slate-300 hover:text-white border border-white/10">
          <Menu className="w-5 h-5" />
        </button>
      </div>

      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div 
            initial={{ x: "-100%", opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: "-100%", opacity: 0 }}
            transition={{ type: "spring", bounce: 0, duration: 0.4 }}
            className="absolute inset-y-2 left-2 w-72 max-w-[calc(100vw-16px)] bg-slate-950/95 backdrop-blur-3xl border border-white/10 rounded-3xl shadow-2xl flex flex-col z-[100] md:hidden"
          >
            <SidebarContent />
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsMobileMenuOpen(false)}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden rounded-3xl"
          />
        )}
      </AnimatePresence>

      <aside className="hidden md:flex w-72 bg-slate-950/70 backdrop-blur-2xl border border-white/10 rounded-[32px] shadow-2xl flex flex-col z-20 overflow-hidden relative">
        <SidebarContent />
      </aside>

      <main className="flex-1 bg-slate-950/70 backdrop-blur-2xl border border-white/10 rounded-3xl md:rounded-[32px] shadow-2xl relative overflow-hidden flex flex-col z-10">
        <div className="h-full w-full relative overflow-y-auto custom-scrollbar">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab + (activeLocationId || 'all')} 
              initial={{ opacity: 0, scale: 0.98, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.98, y: -10 }}
              transition={{ duration: 0.25, ease: "easeOut" }}
              className="h-full min-h-full"
            >
              {activeTab === 'risk' && <RiskTab locations={locations} />}
              {activeTab === 'pressure' && <PressureTab locations={locations} />}
              {activeTab === 'temperature' && <TemperatureTab locations={locations} />}
              {activeTab === 'moon' && <MoonTab locations={locations} />}
              {activeTab === 'map' && <MapTab locations={locations} />}
              {activeTab === 'camera' && <CameraTab locations={locations} activeLocationId={activeLocationId} />}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </motion.div>
  );
}

// ==========================================
// SEKMELER (TABS)
// ==========================================

function RiskTab({ locations }) {
  const criticalCount = locations.filter(l => l.status === 'Kritik').length;

  return (
    <div className="p-4 md:p-10">
      <h2 className="text-2xl md:text-3xl font-bold text-white mb-6 md:mb-8 tracking-tight">Genel Risk Durumu</h2>
      
      {criticalCount > 0 ? (
        <div className="bg-red-950/40 backdrop-blur-md border border-red-500/30 p-4 md:p-6 rounded-2xl shadow-[0_0_30px_rgba(239,68,68,0.15)] mb-8 flex flex-col md:flex-row items-start gap-4 md:gap-5">
          <div className="bg-red-500/20 p-3 rounded-full flex-shrink-0 animate-pulse">
            <AlertTriangle className="w-6 h-6 md:w-8 md:h-8 text-red-400" />
          </div>
          <div>
            <h3 className="text-lg md:text-xl font-bold text-red-300">DİKKAT! Kritik Su Seviyesi Tespit Edildi</h3>
            <p className="text-sm md:text-base text-red-200/70 mt-2 leading-relaxed">Sistem {criticalCount} konumda eşik değerini (150cm) aşan su seviyesi algıladı. Erken uyarı protokolleri devrede.</p>
          </div>
        </div>
      ) : (
        <div className="bg-green-950/30 backdrop-blur-md border border-green-500/20 p-4 md:p-6 rounded-2xl mb-8 flex flex-col md:flex-row items-start gap-4 md:gap-5">
          <div className="bg-green-500/20 p-3 rounded-full flex-shrink-0">
            <ShieldAlert className="w-6 h-6 md:w-8 md:h-8 text-green-400" />
          </div>
          <div>
            <h3 className="text-lg md:text-xl font-bold text-green-300">Tüm Sistemler Normal</h3>
            <p className="text-sm md:text-base text-green-200/70 mt-2 leading-relaxed">Ölçüm yapılan tüm konumlarda su seviyeleri güvenli eşikler içerisindedir.</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 md:gap-6">
        {locations.map(loc => (
          <div key={loc.id} className={`p-5 rounded-2xl backdrop-blur-md transition-all duration-300 border ${loc.status === 'Kritik' ? 'bg-red-950/20 border-red-500/40 shadow-[0_0_20px_rgba(239,68,68,0.1)]' : 'bg-slate-900/40 border-white/10 hover:bg-slate-800/60'}`}>
            <h4 className="font-bold text-white text-base md:text-lg mb-1">{loc.name}</h4>
            <p className="text-[10px] md:text-xs text-blue-300/60 mb-4 font-mono bg-blue-900/20 px-2 py-1 rounded inline-block">{loc.latStr} / {loc.lngStr}</p>
            
            <div className="space-y-3">
              <div className="flex justify-between items-end border-b border-white/5 pb-2 md:pb-3">
                <span className="text-xs md:text-sm text-slate-400">Su Seviyesi</span> 
                <span className={`text-xl md:text-2xl font-bold tracking-tight ${loc.status === 'Kritik' ? 'text-red-400' : 'text-blue-400'}`}>{loc.waterLevel} <span className="text-xs md:text-sm font-normal text-slate-500">cm</span></span>
              </div>
              <div className="flex justify-between items-center pt-1">
                <span className="text-xs md:text-sm text-slate-400">Durum</span> 
                <span className={`px-2 py-1 md:px-3 md:py-1 rounded-lg text-[10px] md:text-xs font-bold tracking-wider uppercase ${loc.status === 'Kritik' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-green-500/10 text-green-400 border border-green-500/20'}`}>{loc.status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function PressureTab({ locations }) {
  return (
    <div className="p-4 md:p-10 flex flex-col h-full">
      <div className="flex items-center gap-3 md:gap-4 mb-6 md:mb-10">
        <div className="p-2 md:p-3 bg-blue-500/20 border border-blue-500/30 rounded-xl text-blue-400">
          <Wind className="w-6 h-6 md:w-7 md:h-7" />
        </div>
        <div>
          <h2 className="text-xl md:text-3xl font-bold text-white">Basınç Değerleri</h2>
          <p className="text-slate-400 text-xs md:text-sm mt-1">BMP280 Sensör Ağ Verileri</p>
        </div>
      </div>

      <div className="grid gap-4 md:gap-6 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4">
        {locations.map((loc, idx) => (
          <div key={loc.id} className="bg-slate-900/40 backdrop-blur-md rounded-2xl border border-white/10 relative overflow-hidden group transition-all duration-300 p-6 md:p-8 hover:bg-slate-800/50" style={{ animationDelay: `${idx * 100}ms` }}>
            <div className="absolute w-24 h-24 md:w-32 md:h-32 -right-8 -top-8 md:-right-12 md:-top-12 bg-blue-500/5 rounded-full blur-2xl group-hover:bg-blue-500/10 transition-colors duration-500"></div>
            
            <h3 className="text-base md:text-lg font-bold text-white relative z-10">{loc.name}</h3>
            <p className="text-slate-500 relative z-10 font-mono text-[10px] md:text-xs mb-4 md:mb-8">Sensör ID: BMP-{loc.id}00</p>
            
            <div className="flex items-baseline gap-2 md:gap-3 relative z-10">
              <span className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-blue-300 to-indigo-500 tracking-tighter drop-shadow-lg transition-all duration-300">{loc.pressure}</span>
              <span className="text-sm md:text-base text-slate-400 font-medium">hPa</span>
            </div>
            
            <div className="mt-6 md:mt-10 flex items-center gap-2 px-2 py-1 md:px-3 md:py-1.5 text-[10px] md:text-xs text-green-400 bg-green-500/10 border border-green-500/20 w-fit rounded-lg relative z-10">
              <span className="w-2 h-2 md:w-2.5 md:h-2.5 rounded-full bg-green-400 animate-pulse shadow-[0_0_8px_#4ade80]"></span>
              Aktif
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TemperatureTab({ locations }) {
  return (
    <div className="p-4 md:p-10 flex flex-col h-full">
      <div className="flex items-center gap-3 md:gap-4 mb-6 md:mb-10">
        <div className="p-2 md:p-3 bg-orange-500/20 border border-orange-500/30 rounded-xl text-orange-400">
          <Thermometer className="w-6 h-6 md:w-7 md:h-7" />
        </div>
        <div>
          <h2 className="text-xl md:text-3xl font-bold text-white">Sıcaklık Değerleri</h2>
          <p className="text-slate-400 text-xs md:text-sm mt-1">Çevresel Sensör İzleme</p>
        </div>
      </div>

      <div className="grid gap-4 md:gap-6 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4">
        {locations.map((loc) => (
          <div key={loc.id} className="bg-slate-900/40 backdrop-blur-md rounded-2xl border border-white/10 relative overflow-hidden group transition-all duration-300 p-6 md:p-8 hover:bg-slate-800/50">
            <div className={`absolute top-0 left-0 w-full h-1 md:h-1.5 ${loc.temp > 25 ? 'bg-gradient-to-r from-red-500 to-orange-500' : 'bg-gradient-to-r from-orange-400 to-amber-300'}`}></div>
            
            <h3 className="text-base md:text-lg font-bold text-white mt-2 md:mt-4">{loc.name}</h3>
            <p className="text-slate-500 relative z-10 font-mono text-[10px] md:text-xs mb-4 md:mb-6">TEMP-{loc.id}00</p>

            <div className="flex items-center justify-between mt-2 md:mt-4">
              <div className="flex items-baseline gap-1 md:gap-2">
                <span className="text-4xl md:text-5xl font-black text-white tracking-tighter transition-all duration-500">{loc.temp}</span>
                <span className="text-xl md:text-2xl text-slate-400 font-light">°C</span>
              </div>
              <Thermometer className={`w-8 h-8 md:w-12 md:h-12 ${loc.temp > 25 ? 'text-red-400' : 'text-orange-400/50'} group-hover:scale-110 transition-all duration-300`} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MoonTab({ locations }) {
  return (
    <div className="p-4 md:p-10 relative h-full">
      <div className="relative z-10 mb-6 md:mb-10 flex flex-col md:flex-row md:items-end justify-between gap-4 md:gap-6">
        <div>
          <h2 className="text-2xl md:text-3xl font-bold text-white flex items-center gap-2 md:gap-3">
            <Moon className="w-6 h-6 md:w-8 md:h-8 text-indigo-400 drop-shadow-[0_0_15px_rgba(129,140,248,0.6)]" /> Astronomik Veriler
          </h2>
          <p className="text-slate-400 mt-1 md:mt-2 font-mono text-xs md:text-sm tracking-wider">ephem_engine_v1.0</p>
        </div>
        <div className="bg-indigo-950/40 border border-indigo-500/30 px-4 md:px-6 py-2 md:py-3 rounded-2xl flex justify-between md:justify-start md:gap-8 shadow-lg backdrop-blur-md">
          <div><span className="block text-[8px] md:text-[10px] text-indigo-300/70 uppercase font-bold tracking-wider mb-0.5 md:mb-1">Evre</span> <span className="font-bold text-white text-sm md:text-base">Şişkin Ay (%82)</span></div>
          <div><span className="block text-[8px] md:text-[10px] text-indigo-300/70 uppercase font-bold tracking-wider mb-0.5 md:mb-1">Çekim Etkisi</span> <span className="font-bold text-indigo-300 text-sm md:text-base">1.14x</span></div>
        </div>
      </div>

      <div className="relative z-10 grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 md:gap-6 pb-6">
        {locations.map((loc) => (
          <div key={loc.id} className="bg-slate-900/60 backdrop-blur-xl rounded-[20px] md:rounded-[24px] border border-white/10 overflow-hidden flex flex-col group hover:border-indigo-500/30 transition-colors">
            <div className="bg-slate-950/80 px-4 py-3 md:px-5 md:py-4 border-b border-white/5 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-white text-xs md:text-sm truncate">{loc.name}</h3>
                <p className="text-[9px] md:text-[10px] text-indigo-400/70 mt-0.5 md:mt-1 font-mono tracking-widest">{loc.latStr} / {loc.lngStr}</p>
              </div>
            </div>

            <div className="py-8 md:py-12 flex justify-center items-center bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-800 to-slate-900 relative overflow-hidden">
              <div className="absolute bottom-0 w-full h-1/2 bg-gradient-to-t from-indigo-500/10 to-transparent"></div>
              
              <div 
                className="w-24 h-24 md:w-32 md:h-32 rounded-full bg-slate-200 shadow-[0_0_30px_rgba(255,255,255,0.15),inset_-10px_0_30px_rgba(0,0,0,0.9)] md:shadow-[0_0_40px_rgba(255,255,255,0.15),inset_-15px_0_40px_rgba(0,0,0,0.9)] relative transition-transform duration-1000"
                style={{ transform: `rotate(${loc.moonData.tilt}deg)` }}
              >
                <div className="absolute w-4 h-4 md:w-6 md:h-6 rounded-full bg-slate-500/30 top-3 md:top-4 left-6 md:left-10"></div>
                <div className="absolute w-6 h-6 md:w-10 md:h-10 rounded-full bg-slate-500/30 bottom-4 md:bottom-6 right-4 md:right-6"></div>
                <div className="absolute top-0 right-0 w-1/2 h-full bg-black/80 rounded-r-full blur-[3px] md:blur-[4px] mix-blend-multiply"></div>
              </div>
              <div className="absolute bottom-0 w-full h-px bg-indigo-500/30 shadow-[0_0_10px_rgba(99,102,241,0.5)]"></div>
              <div className="absolute bottom-1 md:bottom-2 right-2 md:right-4 text-[8px] md:text-[9px] text-indigo-300/50 uppercase tracking-widest font-bold">Ufuk Çizgisi</div>
            </div>

            <div className="p-4 md:p-5 bg-slate-900/40 space-y-3 md:space-y-4 flex-1">
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-[10px] md:text-xs flex items-center gap-1 md:gap-2 uppercase tracking-wider font-bold"><Navigation className="w-3 h-3 md:w-4 md:h-4 text-slate-500" /> Yükseklik</span>
                <span className="font-mono text-white bg-slate-800 px-2 py-0.5 md:py-1 rounded text-xs md:text-sm">{loc.moonData.altitude}°</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-[10px] md:text-xs flex items-center gap-1 md:gap-2 uppercase tracking-wider font-bold"><Compass className="w-3 h-3 md:w-4 md:h-4 text-slate-500" /> Azimuth</span>
                <span className="font-mono text-white bg-slate-800 px-2 py-0.5 md:py-1 rounded text-xs md:text-sm">{loc.moonData.azimuth}°</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MapTab({ locations }) {
  const mapRef = useRef(null);
  const markersRef = useRef({});

  useEffect(() => {
    if (!document.getElementById('leaflet-css')) {
      const link = document.createElement('link');
      link.id = 'leaflet-css';
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);
    }

    if (!document.getElementById('leaflet-js')) {
      const script = document.createElement('script');
      script.id = 'leaflet-js';
      script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      script.onload = initializeMap;
      document.head.appendChild(script);
    } else {
      initializeMap();
    }

    function initializeMap() {
      if (mapRef.current || !window.L) return;
      const L = window.L;
      
      const isMobile = window.innerWidth < 768;
      const map = L.map('real-map', { zoomControl: false }).setView([39.0, 35.0], isMobile ? 4.5 : 5);
      
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO'
      }).addTo(map);
      
      L.control.zoom({ position: 'bottomright' }).addTo(map);
      mapRef.current = map;
      updateMarkers();
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
        markersRef.current = {};
      }
    };
  }, []);

  useEffect(() => {
    updateMarkers();
  }, [locations]);

  const updateMarkers = () => {
    if (!window.L || !mapRef.current) return;
    const L = window.L;
    const map = mapRef.current;

    locations.forEach(loc => {
      const isCritical = loc.status === 'Kritik';
      const colorClass = isCritical ? 'bg-red-500' : 'bg-blue-500';
      const shadowClass = isCritical ? 'shadow-[0_0_15px_#ef4444]' : 'shadow-[0_0_15px_#3b82f6]';
      
      const popupContent = `
        <div style="font-family: ui-sans-serif, system-ui, sans-serif; min-width: 150px; background-color: #0f172a; color: white; margin: -10px md:-14px; padding: 10px md:14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
          <h4 style="font-weight: bold; font-size: 13px; margin-bottom: 6px; color: #f8fafc;">${loc.name}</h4>
          <span style="background-color: ${isCritical ? 'rgba(239,68,68,0.2)' : 'rgba(59,130,246,0.2)'}; color: ${isCritical ? '#fca5a5' : '#93c5fd'}; border: 1px solid ${isCritical ? 'rgba(239,68,68,0.4)' : 'rgba(59,130,246,0.4)'}; padding: 2px 6px; border-radius: 6px; font-size: 9px; font-weight: bold;">
            ${loc.status}
          </span>
          <div style="margin-top: 10px; font-size: 11px; line-height: 1.6; color: #cbd5e1;">
            <div style="display: flex; justify-content: space-between;"><span>Basınç:</span> <b style="color: white;">${loc.pressure} hPa</b></div>
            <div style="display: flex; justify-content: space-between;"><span>Sıcaklık:</span> <b style="color: white;">${loc.temp} °C</b></div>
            <div style="display: flex; justify-content: space-between; margin-top: 6px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.1);">
              <span style="color: #94a3b8;">Su Sev.:</span> 
              <b style="color: ${isCritical ? '#ef4444' : '#60a5fa'}; font-size: 14px;">${loc.waterLevel} cm</b>
            </div>
          </div>
        </div>
      `;

      if (markersRef.current[loc.id]) {
        const marker = markersRef.current[loc.id];
        marker.setPopupContent(popupContent);
        const iconHtml = `
          <div class="relative">
            <div class="w-4 h-4 md:w-5 md:h-5 rounded-full border-2 border-slate-900 ${colorClass} ${shadowClass} z-10 relative"></div>
            <div class="absolute top-0 left-0 w-4 h-4 md:w-5 md:h-5 rounded-full animate-ping opacity-60 ${colorClass}"></div>
          </div>
        `;
        marker.setIcon(L.divIcon({ html: iconHtml, className: '', iconSize: [20, 20], iconAnchor: [10, 10] }));
      } else {
        const customIcon = L.divIcon({
          html: `
            <div class="relative">
              <div class="w-4 h-4 md:w-5 md:h-5 rounded-full border-2 border-slate-900 ${colorClass} ${shadowClass} z-10 relative"></div>
              <div class="absolute top-0 left-0 w-4 h-4 md:w-5 md:h-5 rounded-full animate-ping opacity-60 ${colorClass}"></div>
            </div>
          `,
          className: '', 
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        });

        const marker = L.marker([loc.lat, loc.lng], { icon: customIcon }).addTo(map);
        marker.bindPopup(popupContent, { className: 'custom-dark-popup' });
        markersRef.current[loc.id] = marker;
      }
    });
  };

  return (
    <div className="h-full w-full relative">
      <div className="absolute top-4 left-4 md:top-6 md:left-6 bg-slate-950/80 backdrop-blur-xl px-3 py-2 md:px-5 md:py-4 rounded-xl md:rounded-2xl border border-white/10 shadow-2xl z-[400] pointer-events-none">
        <h3 className="font-bold text-white flex items-center gap-1.5 md:gap-2 text-sm md:text-base"><MapIcon className="w-4 h-4 md:w-5 md:h-5 text-blue-400"/> Canlı Harita</h3>
        <p className="text-[10px] md:text-xs text-slate-400 mt-0.5 md:mt-1 hidden sm:block">Türkiye Kıyı Gözlem İstasyonları</p>
      </div>
      <div id="real-map" className="w-full h-full z-0 bg-slate-900"></div>
      <style dangerouslySetInnerHTML={{__html: `
        .leaflet-popup-content-wrapper { background: transparent; box-shadow: none; padding: 0; }
        .leaflet-popup-tip { background: #0f172a; border-bottom: 1px solid rgba(255,255,255,0.1); border-right: 1px solid rgba(255,255,255,0.1); }
      `}} />
    </div>
  );
}

function CameraTab({ locations, activeLocationId }) {
  const displayLocations = activeLocationId ? locations.filter(l => l.id === activeLocationId) : locations;
  const isSingle = displayLocations.length === 1;

  const cameraFeeds = [
    "https://picsum.photos/seed/tidesense1/1200/800",
    "https://picsum.photos/seed/tidesense2/1200/800",
    "https://picsum.photos/seed/tidesense3/1200/800",
    "https://picsum.photos/seed/tidesense4/1200/800"
  ];

  return (
    <div className="p-4 md:p-10 min-h-full flex flex-col">
      <div className="flex items-center justify-between mb-6 md:mb-10">
        <div>
          <h2 className="text-xl md:text-3xl font-bold text-white flex items-center gap-2 md:gap-3">
            <Camera className="w-6 h-6 md:w-8 md:h-8 text-blue-400" /> İstasyon Kameraları
          </h2>
          <p className="text-slate-400 text-[10px] md:text-sm mt-1 md:mt-2 font-mono tracking-wider">{isSingle ? 'DETAYLI ANALİZ' : 'OPENCV_VISION_V2'}</p>
        </div>
        <div className="bg-red-500/10 border border-red-500/30 px-2 py-1.5 md:px-4 md:py-2 rounded-lg md:rounded-xl flex items-center gap-2 md:gap-3 shadow-[0_0_15px_rgba(239,68,68,0.2)]">
          <span className="w-2 h-2 md:w-2.5 md:h-2.5 rounded-full bg-red-500 animate-pulse shadow-[0_0_8px_#ef4444]"></span>
          <span className="text-red-400 text-[10px] md:text-sm font-bold tracking-widest uppercase">REC</span>
        </div>
      </div>

      <div className={`grid gap-4 md:gap-8 ${isSingle ? 'grid-cols-1 max-w-5xl mx-auto w-full' : 'grid-cols-1 lg:grid-cols-2'}`}>
        {displayLocations.map((loc) => (
          <div key={loc.id} className="bg-slate-900/40 backdrop-blur-md rounded-2xl overflow-hidden border border-white/10 shadow-2xl flex flex-col group p-1.5 md:p-2">
            <div className="bg-slate-950/80 px-3 py-2 md:px-4 md:py-3 flex justify-between items-center border-b border-white/5">
              <h3 className={`${isSingle ? 'text-lg md:text-xl' : 'text-xs md:text-sm'} text-white font-bold truncate pr-2 tracking-wide`}>{loc.name}</h3>
              <span className={`flex-shrink-0 text-[9px] md:text-[10px] border px-2 py-1 md:px-3 md:py-1 rounded-md md:rounded-lg font-bold tracking-wider ${loc.status === 'Kritik' ? 'text-red-400 border-red-400/30 bg-red-400/10' : 'text-green-400 border-green-400/30 bg-green-400/10'}`}>
                {loc.status === 'Kritik' ? 'DİKKAT - YÜKSEK' : 'İYİ'}
              </span>
            </div>
            
            <div className="relative aspect-video bg-black rounded-xl overflow-hidden border border-white/5">
              <img 
                src={cameraFeeds[loc.id - 1]} 
                alt={`${loc.name} Kamera`}
                className="w-full h-full object-cover opacity-70 group-hover:opacity-100 transition-opacity duration-700"
              />
              
              <div className={`absolute w-full h-[1px] md:h-[2px] shadow-[0_0_15px] z-10 transition-all duration-1000 ${loc.status === 'Kritik' ? 'bg-red-500 shadow-red-500' : 'bg-blue-500 shadow-blue-500'}`} style={{ bottom: `${(loc.waterLevel / 200) * 100}%` }}></div>
              
              <div className="absolute top-2 left-2 md:top-4 md:left-4 flex flex-col gap-2">
                <div className={`text-white ${isSingle ? 'text-xs md:text-sm' : 'text-[8px] md:text-[10px]'} font-mono bg-black/60 backdrop-blur-sm px-2 py-1 md:px-3 md:py-1.5 rounded border border-white/10`}>
                  FPS: {Math.floor(Math.random() * 5) + 25} | 1080p
                </div>
              </div>
              
              <div className={`absolute bottom-2 left-2 md:bottom-4 md:left-4 text-white ${isSingle ? 'text-lg md:text-2xl px-4 py-2 md:px-6 md:py-3' : 'text-[10px] md:text-sm px-2 py-1 md:px-3 md:py-1.5'} font-mono font-bold rounded-lg border backdrop-blur-md transition-colors ${loc.status === 'Kritik' ? 'bg-red-500/30 border-red-500/50 text-red-200 shadow-[0_0_20px_rgba(239,68,68,0.5)]' : 'bg-slate-900/60 border-white/20'}`}>
                OpenCV: {loc.waterLevel} cm
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
