import { useState, useRef, useEffect, useMemo } from 'react';
import { 
  useGetPhotosQuery, 
  useGetFilterOptionsQuery, 
  useSearchPhotosMutation, 
  useUploadPhotoMutation,
  useDeletePhotoMutation
} from '../api/client';
import type { Photo } from '../api/client';
import { motion, AnimatePresence } from 'framer-motion';
import { SlidersHorizontal, Calendar, Smile, MapPin, Search, Upload, X, ChevronRight, Trash2 } from 'lucide-react';

interface FilterState {
  emotions: string[];
  location: string | null;
  objects: string[];
  customObject: string;
}

export default function Gallery() {
  const { data: allPhotos = [], isLoading: loadingPhotos } = useGetPhotosQuery();
  const { data: options } = useGetFilterOptionsQuery();
  const [searchPhotos, { data: searchResults, isLoading: searching }] = useSearchPhotosMutation();
  const [uploadPhoto, { isLoading: uploading }] = useUploadPhotoMutation();
  const [deletePhoto] = useDeletePhotoMutation();
  
  const [query, setQuery] = useState('');
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(null);
  const [uploadProgress, setUploadProgress] = useState<{current: number, total: number} | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const filterPanelRef = useRef<HTMLDivElement>(null);

  const [filters, setFilters] = useState<FilterState>({
    emotions: [],
    location: null,
    objects: [],
    customObject: ''
  });

  // Filtreler veya Query değiştiğinde otomatik ara
  useEffect(() => {
    const triggerSearch = async () => {
      const activeObjects = [...filters.objects];
      if (filters.customObject) activeObjects.push(filters.customObject);

      await searchPhotos({
        query: query || undefined,
        filters: {
          emotions: filters.emotions.length > 0 ? filters.emotions : undefined,
          location_types: filters.location ? [filters.location === 'Ev' ? 'iç mekan' : 'dış mekan'] : undefined,
          objects: activeObjects.length > 0 ? activeObjects : undefined,
        }
      }).unwrap();
    };

    const timer = setTimeout(triggerSearch, 300);
    return () => clearTimeout(timer);
  }, [query, filters, searchPhotos]);

  const photos = query || filters.emotions.length || filters.location || filters.customObject || filters.objects.length
    ? searchResults || []
    : allPhotos;

  const toggleEmotion = (emotion: string) => {
    setFilters(prev => ({
      ...prev,
      emotions: prev.emotions.includes(emotion) 
        ? prev.emotions.filter(e => e !== emotion) 
        : [...prev.emotions, emotion]
    }));
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      setUploadProgress({ current: 0, total: files.length });
      
      try {
        for (let i = 0; i < files.length; i++) {
          setUploadProgress({ current: i + 1, total: files.length });
          await uploadPhoto(files[i]).unwrap();
        }
      } catch (err) {
        console.error(err);
        alert('Bazı fotoğraflar yüklenemedi.');
      } finally {
        setUploadProgress(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="min-h-screen bg-[#F8F9FB] text-slate-900 font-sans selection:bg-blue-100 pb-20">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none opacity-40">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] rounded-full bg-blue-200 blur-[120px]" />
        <div className="absolute top-[20%] -right-[5%] w-[30%] h-[30%] rounded-full bg-purple-100 blur-[100px]" />
      </div>

      <div className="relative max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <header className="flex justify-between items-center mb-16">
          <div className="flex items-center gap-3">
            <h1 className="text-4xl font-serif text-slate-800 tracking-tight font-medium">Aren Photo Memory</h1>
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-200">
              <span className="text-xs font-bold italic">AI</span>
            </div>
          </div>
          <div>
            <input 
              type="file" 
              className="hidden" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              accept="image/*" 
              multiple 
            />
            <button 
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="group flex items-center gap-2 bg-[#1E40AF] text-white px-8 py-3.5 rounded-2xl font-semibold shadow-xl shadow-blue-900/10 hover:bg-blue-800 transition-all active:scale-95 disabled:opacity-50"
            >
              <Upload className="h-5 w-5 opacity-80" />
              {uploadProgress ? `Uploading (${uploadProgress.current}/${uploadProgress.total})...` : 'Upload New Memories'}
            </button>
          </div>
        </header>

        {/* Search & Dynamic Filter Section */}
        <div className="max-w-4xl mx-auto mb-16 relative">
          <div className="relative group">
            <div className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors">
              <Search className="h-6 w-6" />
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search memories, emotions, people..."
              className="w-full h-20 pl-16 pr-32 rounded-[2.5rem] bg-white/70 backdrop-blur-2xl border border-white/50 shadow-2xl shadow-slate-200/50 outline-none text-xl placeholder:text-slate-400 focus:ring-4 focus:ring-blue-500/10 transition-all"
            />
            
            {/* Combined Search/Filter Controls */}
            <div className="absolute right-6 top-1/2 -translate-y-1/2 flex items-center gap-3">
               {searching && (
                 <div className="hidden sm:flex items-center gap-2 bg-blue-50/50 px-3 py-1.5 rounded-full border border-blue-100">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
                    <span className="text-[9px] font-black text-blue-600 uppercase tracking-widest">AI Agent</span>
                 </div>
               )}
               <button 
                onClick={() => setIsFilterOpen(!isFilterOpen)}
                className={`p-4 rounded-2xl transition-all ${isFilterOpen ? 'bg-blue-600 text-white shadow-lg shadow-blue-200 scale-105' : 'bg-slate-50 text-slate-400 hover:bg-white hover:text-blue-600 hover:shadow-md'}`}
               >
                 <SlidersHorizontal className="h-6 w-6" />
               </button>
            </div>
          </div>


          {/* New Animated Glassmorphism Filter Popover */}
          <AnimatePresence>
            {isFilterOpen && (
              <motion.div 
                initial={{ opacity: 0, y: -20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="absolute top-[calc(100%+12px)] left-0 right-0 z-40"
              >
                <div className="mx-auto max-w-2xl bg-white/80 backdrop-blur-3xl rounded-[3rem] border border-white/60 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.1)] p-10 overflow-hidden">
                  <div className="space-y-10">
                    
                    {/* Emotion Section */}
                    <div className="space-y-4">
                      <div className="flex items-center gap-3 text-slate-400">
                        <Smile className="h-5 w-5" />
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em]">Duygu Seçimi</h4>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {options?.emotions.map(e => (
                          <button
                            key={e}
                            onClick={() => toggleEmotion(e)}
                            className={`px-6 py-3 rounded-2xl text-xs font-bold transition-all ${filters.emotions.includes(e) ? 'bg-blue-600 text-white shadow-lg shadow-blue-200' : 'bg-white/50 text-slate-500 hover:bg-white border border-slate-100 capitalize'}`}
                          >
                            {e}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="h-px bg-slate-100 w-full" />

                    {/* Location Section */}
                    <div className="space-y-4">
                      <div className="flex items-center gap-3 text-slate-400">
                        <MapPin className="h-5 w-5" />
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em]">Mekan</h4>
                      </div>
                      <div className="flex gap-2 p-1.5 bg-slate-50/50 rounded-2xl w-fit border border-slate-100">
                        {['Tümü', 'Ev', 'Dış Mekan'].map(loc => (
                          <button
                            key={loc}
                            onClick={() => setFilters(f => ({ ...f, location: loc === 'Tümü' ? null : loc }))}
                            className={`px-8 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${ (loc === 'Tümü' && !filters.location) || filters.location === loc ? 'bg-white text-blue-600 shadow-sm border border-slate-100' : 'text-slate-400 hover:text-slate-600' }`}
                          >
                            {loc}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="h-px bg-slate-100 w-full" />

                    {/* Time & Objects Section */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                      <div className="space-y-4">
                        <div className="flex items-center gap-3 text-slate-400">
                          <Calendar className="h-5 w-5" />
                          <h4 className="text-[10px] font-black uppercase tracking-[0.2em]">Zaman Aralığı</h4>
                        </div>
                        <div className="flex gap-2">
                          {['Son 1 Ay', 'Geçen Yaz'].map(t => (
                            <button key={t} className="px-5 py-3 bg-white/50 text-[10px] font-bold text-slate-500 rounded-2xl border border-slate-100 hover:bg-white transition-all">
                              {t}
                            </button>
                          ))}
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div className="flex items-center gap-3 text-slate-400">
                          <Search className="h-5 w-5" />
                          <h4 className="text-[10px] font-black uppercase tracking-[0.2em]">Özel Nesne</h4>
                        </div>
                        <input 
                          type="text" 
                          value={filters.customObject}
                          onChange={(e) => setFilters(f => ({ ...f, customObject: e.target.value }))}
                          placeholder="Araba, Uçak vb..."
                          className="w-full bg-slate-50/50 border border-slate-100 rounded-2xl px-5 py-3 text-sm font-semibold focus:bg-white focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                        />
                      </div>
                    </div>

                    {/* Reset Button */}
                    <div className="pt-4">
                       <button 
                        onClick={() => {
                          setFilters({ emotions: [], location: null, objects: [], customObject: '' });
                          setQuery('');
                        }}
                        className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2 hover:text-red-500 transition-colors"
                       >
                         <X className="h-3 w-3" /> Filtreleri Temizle
                       </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Gallery Grid */}
        {loadingPhotos && !photos.length ? (
          <div className="flex flex-col items-center justify-center py-32">
            <div className="w-16 h-16 border-4 border-blue-500/10 border-t-blue-600 rounded-full animate-spin mb-4" />
            <p className="text-slate-400 font-medium tracking-[0.2em] text-[10px] font-black uppercase">Analyzing Memories...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10">
            {photos.map(p => (
              <motion.div 
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                key={p.id} 
                onClick={() => setSelectedPhoto(p)}
                className="group relative bg-white rounded-[2.5rem] shadow-sm hover:shadow-2xl transition-all duration-500 cursor-pointer overflow-hidden border border-slate-100"
              >
                <div className="relative aspect-[3/4] overflow-hidden">
                  <img src={`http://localhost:8000${p.file_url}`} alt="Memory" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                  <div className="absolute top-6 left-6 right-6 flex justify-between items-start z-10">
                    <div className="bg-white/40 backdrop-blur-xl border border-white/40 p-4 rounded-3xl shadow-xl max-w-[70%]">
                      <div className="flex flex-col gap-1">
                        <span className="text-[10px] font-bold text-slate-800/60 uppercase tracking-widest">Emotion Index</span>
                        <span className="text-sm font-bold text-slate-800 capitalize">😊 9.2 {p.emotion}</span>
                        <div className="w-full h-1 bg-slate-800/10 rounded-full mt-1 overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full w-[92%]" />
                        </div>
                      </div>
                    </div>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm('Bu fotoğrafı silmek istediğine emin misin? (Bu işlem geri alınamaz)')) {
                          deletePhoto(p.id);
                        }
                      }}
                      className="bg-white/40 backdrop-blur-xl border border-white/40 p-3 rounded-full text-slate-700 hover:text-red-500 hover:bg-white transition-all shadow-xl opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                  {p.relevance !== undefined && (
                    <div className="absolute bottom-6 left-6">
                      <div className="bg-emerald-500 text-white text-[10px] font-black px-4 py-2 rounded-2xl shadow-xl tracking-widest uppercase">
                        %{p.relevance} Match
                      </div>
                    </div>
                  )}
                </div>
                <div className="p-8">
                  <span className="text-slate-300 text-[9px] font-black tracking-widest uppercase block mb-3">
                    {new Date(p.uploaded_at).toLocaleDateString('tr-TR')}
                  </span>
                  <p className="text-slate-600 text-sm leading-relaxed line-clamp-3 font-medium italic">
                    "{p.description}"
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        )}
        
        {/* Modal View (Unchanged but ensuring it still looks premium) */}
        {selectedPhoto && (
          <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-10">
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="absolute inset-0 bg-slate-950/60 backdrop-blur-md" 
                onClick={() => setSelectedPhoto(null)} 
              />
              <motion.div 
                initial={{ opacity: 0, scale: 0.9, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.9, y: 20 }}
                className="relative w-full max-w-6xl bg-white rounded-[3rem] shadow-2xl overflow-hidden flex flex-col lg:flex-row max-h-[90vh]"
              >
                <button onClick={() => setSelectedPhoto(null)} className="absolute top-8 right-8 z-20 bg-slate-900/10 hover:bg-slate-900/20 text-slate-900 p-3 rounded-2xl backdrop-blur-md transition-all">
                  <X className="h-6 w-6" />
                </button>
                <div className="w-full lg:w-[60%] bg-[#F3F4F6] flex items-center justify-center overflow-hidden border-r border-slate-100">
                  <img src={`http://localhost:8000${selectedPhoto.file_url}`} alt="Full memory" className="w-full h-full object-contain p-6" />
                </div>
                <div className="w-full lg:w-[40%] p-10 sm:p-16 overflow-y-auto bg-white">
                  <div className="flex gap-2 mb-8">
                    <span className="bg-blue-600 text-white text-[9px] px-4 py-2 rounded-full font-black uppercase tracking-widest">{selectedPhoto.emotion}</span>
                    <span className="bg-slate-100 text-slate-500 text-[9px] px-4 py-2 rounded-full font-bold uppercase tracking-widest">{new Date(selectedPhoto.uploaded_at).toLocaleDateString('tr-TR')}</span>
                  </div>
                  <h2 className="text-4xl font-serif font-medium text-slate-800 mb-10 leading-tight">Memory Analysis</h2>
                  <div className="space-y-10">
                    <div className="relative">
                      <div className="absolute -left-6 top-0 bottom-0 w-1 bg-blue-500 rounded-full opacity-20" />
                      <h3 className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4">Detailed Description</h3>
                      <p className="text-slate-600 leading-relaxed text-xl font-medium italic">"{selectedPhoto.description}"</p>
                    </div>
                    <div className="grid grid-cols-2 gap-6">
                      <div className="bg-slate-50 p-6 rounded-[2rem] border border-slate-100">
                        <h4 className="text-[9px] font-black text-slate-400 uppercase mb-2 tracking-widest">Activity</h4>
                        <p className="text-slate-800 font-bold text-lg">{selectedPhoto.activity}</p>
                      </div>
                      <div className="bg-slate-50 p-6 rounded-[2rem] border border-slate-100">
                        <h4 className="text-[9px] font-black text-slate-400 uppercase mb-2 tracking-widest">Location</h4>
                        <p className="text-slate-800 font-bold text-lg">{selectedPhoto.location_detail}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
