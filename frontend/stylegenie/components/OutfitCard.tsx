
import { useState } from "react";
import { Button } from "./ui/button";
import { Heart, ShoppingCart } from "lucide-react";

interface OutfitCardProps {
  image: string;
  title: string;
}

const OutfitCard = ({ image, title }: OutfitCardProps) => {
  const [liked, setLiked] = useState(false);
  
  return (
    <div className="outfit-card">
      <div className="aspect-[3/4] overflow-hidden rounded-md mb-3">
        <img 
          src={image} 
          alt={title} 
          className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
        />
      </div>
      
      <h3 className="font-medium mb-3">{title}</h3>
      
      <div className="flex justify-between items-center">
        <Button variant="outline" size="sm" className="gap-1">
          <ShoppingCart className="h-4 w-4" />
          <span className="hidden sm:inline">Add All</span>
        </Button>
        
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => setLiked(!liked)}
          className={`${liked ? 'text-accent' : ''}`}
        >
          <Heart className={`h-4 w-4 mr-1 ${liked ? 'fill-current' : ''}`} />
          <span className="hidden sm:inline">Save</span>
        </Button>
      </div>
    </div>
  );
};

export default OutfitCard;
