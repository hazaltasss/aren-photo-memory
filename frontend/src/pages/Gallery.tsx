import { useState, useRef } from 'react';
import { useGetPhotosQuery, useSearchPhotosMutation, useUploadPhotoMutation, Photo } from '../api/client';

export default function Gallery() {
  const { data: allPhotos = [], isLoading: loadingPhotos } = useGetPhotosQuery();
  const [searchPhotos, { data: searchResults, isLoading: searching }] = useSearchPhotosMutation();
  const [uploadPhoto, { isLoading: uploading }] = useUploadPhotoMutation();
  
  const [query, setQuery] = useState('');
  const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const photos = query && searchResults ? searchResults : allPhotos;

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      await searchPhotos(query);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      try {
        await uploadPhoto(e.target.files[0]).unwrap();
      } catch (err) {
        console.error(err);
        alert('Upload failed');
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Aren Photo Memory</h1>
        <div>
          <input 
            type="file" 
            className="hidden" 
            ref={fileInputRef} 
            onChange={handleFileChange}
            accept="image/*"
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="bg-blue-600 text-white px-6 py-2.5 rounded-full font-semibold shadow-lg shadow-blue-200 hover:bg-blue-700 hover:shadow-xl disabled:opacity-50 cursor-pointer transition-all active:scale-95"
          >
            {uploading ? 'Analyzing...' : 'Upload Memory'}
          </button>
        </div>
      </header>

      <form onSubmit={handleSearch} className="mb-12">
        <div className="relative group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search memories (e.g. 'Aren laughing with his ball')"
            className="w-full p-5 pl-7 rounded-2xl border-none bg-white shadow-xl shadow-slate-200/50 focus:ring-2 focus:ring-blue-500 outline-none text-lg transition-all"
          />
          {searching && (
            <div className="absolute right-5 top-1/2 -translate-y-1/2">
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-500 border-t-transparent"></div>
            </div>
          )}
        </div>
      </form>

      {loadingPhotos && !photos.length ? (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <div className="animate-pulse flex space-x-4">
            <div className="rounded-full bg-slate-200 h-10 w-10"></div>
          </div>
          <p className="text-slate-400 font-medium">Finding your memories...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {photos.map(p => (
            <div 
              key={p.id} 
              onClick={() => setSelectedPhoto(p)}
              className="group bg-white rounded-3xl shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 cursor-pointer overflow-hidden border border-slate-50"
            >
              <div className="relative aspect-[4/5] overflow-hidden">
                <img 
                  src={`http://localhost:8000${p.file_url}`} 
                  alt="Memory" 
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" 
                />
                <div className="absolute top-4 left-4">
                   <span className="bg-white/90 backdrop-blur-md text-slate-800 text-xs px-3 py-1.5 rounded-full font-bold shadow-sm uppercase tracking-wider">
                    {p.emotion}
                  </span>
                </div>
              </div>
              <div className="p-6">
                <div className="flex justify-between items-start mb-3">
                   <span className="text-slate-400 text-xs font-medium">
                    {new Date(p.uploaded_at).toLocaleDateString('tr-TR')}
                  </span>
                  {p.is_smiling && <span className="text-xl">😊</span>}
                </div>
                <p className="text-slate-600 text-sm leading-relaxed line-clamp-3 italic">
                  "{p.description}"
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {!loadingPhotos && photos.length === 0 && !uploading && (
        <div className="text-center py-20 bg-white rounded-3xl border-2 border-dashed border-slate-100">
          <p className="text-slate-400 text-lg">No memories found yet. Add the first one!</p>
        </div>
      )}

      {/* Modal View */}
      {selectedPhoto && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 md:p-10">
          <div 
            className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm"
            onClick={() => setSelectedPhoto(null)}
          ></div>
          <div className="relative w-full max-w-5xl bg-white rounded-[2rem] shadow-2xl overflow-hidden flex flex-col md:flex-row animate-in fade-in zoom-in duration-300 max-h-[90vh]">
            <button 
              onClick={() => setSelectedPhoto(null)}
              className="absolute top-6 right-6 z-10 bg-white/20 hover:bg-white/40 text-white p-2 rounded-full backdrop-blur-md transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            <div className="w-full md:w-3/5 bg-slate-100 flex items-center justify-center overflow-hidden">
              <img 
                src={`http://localhost:8000${selectedPhoto.file_url}`} 
                alt="Full memory" 
                className="w-full h-full object-contain" 
              />
            </div>
            
            <div className="w-full md:w-2/5 p-8 sm:p-12 overflow-y-auto bg-white">
              <div className="mb-8">
                <div className="flex gap-2 mb-4">
                  <span className="bg-blue-50 text-blue-600 text-xs px-3 py-1 rounded-full font-bold uppercase tracking-widest">
                    {selectedPhoto.emotion}
                  </span>
                  <span className="bg-slate-50 text-slate-500 text-xs px-3 py-1 rounded-full font-medium">
                    {new Date(selectedPhoto.uploaded_at).toLocaleDateString('tr-TR')}
                  </span>
                </div>
                <h2 className="text-2xl font-bold text-slate-800 mb-6 leading-tight">Memory Details</h2>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Description</h3>
                    <p className="text-slate-600 leading-relaxed text-lg italic">"{selectedPhoto.description}"</p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase mb-1">Emotion</h4>
                      <p className="text-slate-700 font-semibold">{selectedPhoto.emotion} {selectedPhoto.is_smiling ? '😊' : ''}</p>
                    </div>
                    <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase mb-1">Uploaded</h4>
                      <p className="text-slate-700 font-semibold">{new Date(selectedPhoto.uploaded_at).toLocaleTimeString('tr-TR', {hour: '2-digit', minute:'2-digit'})}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="pt-8 border-t border-slate-100">
                <p className="text-slate-400 text-sm">Memory ID: <span className="font-mono text-xs">{selectedPhoto.id.split('-')[0]}...</span></p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
