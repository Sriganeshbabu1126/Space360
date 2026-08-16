import React, { useState, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { X, ChevronLeft, ChevronRight, Maximize2 } from 'lucide-react';

export interface IssuePhoto {
  id: string;
  photo_url: string;
  uploaded_by: string;
  created_at: string;
}

interface PhotoGalleryProps {
  photos: IssuePhoto[];
  issueTitle: string;
}

const PhotoGallery: React.FC<PhotoGalleryProps> = ({ photos, issueTitle }) => {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  const handleClose = useCallback(() => {
    setSelectedIndex(null);
  }, []);

  const handleNext = useCallback(() => {
    if (selectedIndex !== null && selectedIndex < photos.length - 1) {
      setSelectedIndex(selectedIndex + 1);
    }
  }, [selectedIndex, photos.length]);

  const handlePrev = useCallback(() => {
    if (selectedIndex !== null && selectedIndex > 0) {
      setSelectedIndex(selectedIndex - 1);
    }
  }, [selectedIndex]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (selectedIndex === null) return;
      if (e.key === 'Escape') handleClose();
      if (e.key === 'ArrowRight') handleNext();
      if (e.key === 'ArrowLeft') handlePrev();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedIndex, handleClose, handleNext, handlePrev]);

  if (!photos || photos.length === 0) {
    return (
      <div className="text-sm text-gray-500 italic p-4 bg-gray-50 rounded-xl border border-gray-100 text-center">
        No photos attached to this issue.
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {photos.map((photo, index) => (
          <div 
            key={photo.id} 
            className="group relative cursor-pointer rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow bg-gray-100 aspect-square"
            onClick={(e) => {
              e.stopPropagation();
              console.log(`Clicked photo ${index}`);
              setSelectedIndex(index);
            }}
          >
            <img 
              src={photo.photo_url} 
              alt={`Evidence for ${issueTitle}`} 
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
              <Maximize2 className="text-white opacity-0 group-hover:opacity-100 transition-opacity w-8 h-8 drop-shadow-lg" />
            </div>
            <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/70 to-transparent pointer-events-none">
              <div className="text-white text-xs font-medium truncate">
                {new Date(photo.created_at).toLocaleString(undefined, { 
                  month: 'short', day: 'numeric', year: 'numeric', 
                  hour: 'numeric', minute: '2-digit' 
                })}
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedIndex !== null && typeof document !== 'undefined' && createPortal(
        <div className="fixed inset-0 bg-black/80 z-50 flex flex-col items-center justify-center" onClick={handleClose}>
          <button 
            className="absolute top-4 right-4 p-2 text-white/70 hover:text-white hover:bg-white/10 rounded-full transition-colors z-10 min-h-[44px] min-w-[44px] flex items-center justify-center"
            onClick={handleClose}
          >
            <X className="w-6 h-6" />
          </button>

          <div 
            className="relative flex-1 w-full max-w-6xl flex items-center justify-center p-0 md:p-8"
            onClick={e => e.stopPropagation()}
          >
            <img 
              src={photos[selectedIndex].photo_url} 
              alt={`Evidence for ${issueTitle}`} 
              className="max-w-full max-h-full object-contain drop-shadow-2xl"
            />

            <button 
              className="absolute left-2 md:left-4 p-3 text-white/70 hover:text-white hover:bg-white/10 rounded-full transition-colors disabled:opacity-30 disabled:hover:bg-transparent min-h-[44px] min-w-[44px] flex items-center justify-center bg-black/20 md:bg-transparent"
              onClick={handlePrev}
              disabled={selectedIndex === 0}
            >
              <ChevronLeft className="w-6 h-6 md:w-8 md:h-8" />
            </button>
            <button 
              className="absolute right-2 md:right-4 p-3 text-white/70 hover:text-white hover:bg-white/10 rounded-full transition-colors disabled:opacity-30 disabled:hover:bg-transparent min-h-[44px] min-w-[44px] flex items-center justify-center bg-black/20 md:bg-transparent"
              onClick={handleNext}
              disabled={selectedIndex === photos.length - 1}
            >
              <ChevronRight className="w-6 h-6 md:w-8 md:h-8" />
            </button>
          </div>

          <div 
            className="w-full bg-black/80 text-white p-4 flex flex-col md:flex-row justify-between items-center text-sm"
            onClick={e => e.stopPropagation()}
          >
            <div className="font-medium mb-2 md:mb-0">
              {selectedIndex + 1} of {photos.length}
            </div>
            <div className="text-gray-300 text-center md:text-right">
              Uploaded by {photos[selectedIndex].uploaded_by.split('@')[0]} on {new Date(photos[selectedIndex].created_at).toLocaleDateString()}
              <div className="text-xs text-gray-500 mt-1">Use ESC to close, arrows to navigate</div>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
};

export default PhotoGallery;
