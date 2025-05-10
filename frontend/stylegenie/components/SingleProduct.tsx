
import { Heart } from "lucide-react";
import { Button } from "./ui/button";
import { useState } from "react";

interface FashionItemProps {
  image: string;
  price: string;
  name?: string;
  onClick?: () => void;
}

const FashionItem = ({ image, price, name, onClick }: FashionItemProps) => {
  const [liked, setLiked] = useState(false);
  
  const toggleLike = (e: React.MouseEvent) => {
    e.stopPropagation();
    setLiked(!liked);
  };
  
  return (
    <div 
      className="fashion-item cursor-pointer" 
      onClick={onClick}
    >
      <div className="aspect-square overflow-hidden">
        <img src={image} alt={name || "Fashion item"} className="w-full h-full object-cover" />
      </div>
      
      <Button
        variant="ghost"
        size="icon"
        onClick={toggleLike}
        className={`absolute top-3 right-3 h-8 w-8 rounded-full bg-white/80 shadow-sm ${liked ? 'text-accent' : 'text-muted-foreground'}`}
      >
        <Heart className={`h-4 w-4 ${liked ? 'fill-current' : ''}`} />
      </Button>
      
      <div className="price-tag">{price}</div>
      
      {name && (
        <div className="p-3">
          <p className="text-sm font-medium truncate">{name}</p>
        </div>
      )}
    </div>
  );
};

export default FashionItem;
