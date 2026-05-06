import { useState, useRef } from 'react';
import { useGetPhotosQuery, useSearchPhotosMutation, useUploadPhotoMutation } from '../api/client';

export default function Gallery() {
  const { data: allPhotos = [], isLoading: loadingPhotos } = useGetPhotosQuery();
  const [searchPhotos, { data: searchResults, isLoading: searching }] = useSearchPhotosMutation();
  const [uploadPhoto, { isLoading: uploading }] = useUploadPhotoMutation();
  
  const [query, setQuery] = useState('');
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
        <h1 className="text-3xl font-bold text-slate-800">Aren Photo Memory</h1>
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
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 cursor-pointer transition"
          >
            {uploading ? 'Analyzing...' : 'Upload Photo'}
          </button>
        </div>
      </header>

      <form onSubmit={handleSearch} className="mb-8">
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (!e.target.value) {
              // clear search when input is empty
            }
          }}
          placeholder="Search memories (e.g. 'Aren in the park laughing')"
          className="w-full p-4 rounded-xl border border-slate-200 shadow-sm focus:ring-2 focus:ring-blue-500 outline-none text-lg"
        />
        {searching && <p className="text-slate-500 text-sm mt-2">Searching...</p>}
      </form>

      {loadingPhotos && !photos.length ? (
        <div className="text-center text-slate-500 mt-20 text-xl">Loading photos...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {photos.map(p => (
            <div key={p.id} className="bg-white rounded-xl shadow-sm overflow-hidden border border-slate-100 hover:shadow-md transition">
              <img src={`http://localhost:8000${p.file_url}`} alt="Memory" className="w-full h-64 object-cover" />
              <div className="p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full font-medium">
                    {p.emotion}
                  </span>
                  {p.is_smiling && <span className="text-xl" title="Smiling">😊</span>}
                </div>
                <p className="text-slate-600 text-sm line-clamp-3">{p.description}</p>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {!loadingPhotos && photos.length === 0 && !uploading && (
        <div className="text-center text-slate-500 mt-20">
          <p className="text-xl">No photos found.</p>
        </div>
      )}
    </div>
  );
}
