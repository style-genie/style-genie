
import { Tab } from "@headlessui/react";
import { cn } from "@/lib/utils";


import FashionItem from "./SingleProduct";
import OutfitCard from "./OutfitCard";

const mockSingleItems = [
  { 
    image: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", 
    price: "75€", 
    name: "Burgundy Handbag" 
  },
  { 
    image: "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", 
    price: "125€", 
    name: "Golden Watch" 
  },
  { 
    image: "https://images.unsplash.com/photo-1542272604-787c3835535d?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", 
    price: "40€", 
    name: "Gray Trousers" 
  },
  { 
    image: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", 
    price: "55€", 
    name: "Red High Heels" 
  },
  { 
    image: "https://images.unsplash.com/photo-1551048632-8df86522cee4?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", 
    price: "30€", 
    name: "White Blouse" 
  },
  { 
    image: "https://images.unsplash.com/photo-1586495777744-4413f21062fa?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", 
    price: "15€", 
    name: "Red Lipstick" 
  },
];

const mockOutfitItems = [
  { 
    image: "https://images.unsplash.com/photo-1503342394128-c104d54dba01?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80", 
    title: "Business Casual" 
  },
  { 
    image: "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80", 
    title: "Elegant Evening" 
  },
  { 
    image: "https://images.unsplash.com/photo-1550639525-c97d455acf70?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80", 
    title: "Office Chic" 
  },
];

const FashionRecommendations = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 py-2">
      <div className="mb-3">
        <h2 className="text-2xl md:text-2xl font-playfair font-medium mb-1">
          Top Picks <span className="text-primary">for You</span>
        </h2>
        <p className="text-xs text-muted-foreground">
          Curated items based on your style preferences
        </p>
      </div>

      <Tab.Group>
        <Tab.List className="flex space-x-4 border-border mb-3">
          <Tab
            className={({ selected }) =>
              cn(
                "px-3 py-1 text-sm font-medium outline-none",
                selected
                  ? "border-b-2 border-primary text-primary"
                  : "text-muted-foreground hover:text-foreground hover:border-b-2 hover:border-muted"
              )
            }
          >
            Individual Items
          </Tab>
          <Tab
            className={({ selected }) =>
              cn(
                "px-3 py-1 text-sm font-medium outline-none",
                selected
                  ? "border-b-2 border-primary text-primary"
                  : "text-muted-foreground hover:text-foreground hover:border-b-2 hover:border-muted"
              )
            }
          >
            Complete Outfits
          </Tab>
        </Tab.List>
        
        <Tab.Panels>
          <Tab.Panel className="animate-fade-in">
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
              {mockSingleItems.slice(0, 6).map((item, index) => (
                <FashionItem
                  key={index}
                  image={item.image}
                  price={item.price}
                  name={item.name}
                />
              ))}
            </div>
          </Tab.Panel>
          
          <Tab.Panel className="animate-fade-in">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {mockOutfitItems.map((outfit, index) => (
                <OutfitCard
                  key={index}
                  image={outfit.image}
                  title={outfit.title}
                />
              ))}
            </div>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
};

export default FashionRecommendations;
