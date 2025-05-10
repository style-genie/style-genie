
import { Camera, Upload, X } from "lucide-react";
import { useState } from "react";
import { Button } from "./ui/button";

const ImageUpload = () => {
  const [image, setImage] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = () => {
    setIsDragging(false);
  };
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      const reader = new FileReader();
      
      reader.onload = (event) => {
        if (event.target && typeof event.target.result === 'string') {
          setImage(event.target.result);
        }
      };
      
      reader.readAsDataURL(file);
    }
  };
  
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();
      
      reader.onload = (event) => {
        if (event.target && typeof event.target.result === 'string') {
          setImage(event.target.result);
        }
      };
      
      reader.readAsDataURL(file);
    }
  };
  
  const removeImage = () => {
    setImage(null);
  };
  
  return (
    <div className="w-full max-w-xl mx-auto mb-3">
      {!image ? (
        <div
          className={`upload-zone py-2 ${isDragging ? 'border-primary bg-secondary' : ''}`}
          style={{  borderColor: '#6000d633',backgroundColor: '#f5f0fa80 !important' }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="flex items-center gap-3">
            <div className="p-1.5 rounded-full bg-primary/10">
              <Camera className="h-4 w-4 text-primary" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-xs">Upload your photo</p>
              <p className="text-xs text-muted-foreground">drag or upload from device</p>
            </div>
            
            <label htmlFor="file-upload">
              <div className="cursor-pointer">
                <Button variant="outline" size="sm" className="h-7 text-xs">
                  <Upload className="h-3 w-3 mr-1" />
                  Browse
                </Button>
                <input
                  id="file-upload"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleFileInput}
                />
              </div>
            </label>
          </div>
        </div>
      ) : (
        <div className="relative rounded-lg overflow-hidden border">
          <img src={image} alt="Uploaded" className="w-full object-cover h-16" />
          <Button 
            variant="destructive" 
            size="icon" 
            className="absolute top-1 right-1 h-5 w-5 rounded-full shadow-md"
            onClick={removeImage}
          >
            <X className="h-2.5 w-2.5" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
