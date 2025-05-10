
import { Search } from "lucide-react";
import { Input } from "./ui/input";
import { useState } from "react";

const SearchBar = () => {
  const [searchQuery, setSearchQuery] = useState("Classy boardroom casual outfit");
  
  return (
    <div className="relative w-full max-w-xl mx-auto mb-8">
      <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
        <Search className="h-5 w-5 text-muted-foreground" />
      </div>
      <Input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search for styles, outfits, or items..."
        className="pl-10 py-6 text-base border bg-search bg-background/80 shadow-sm focus:ring-primary/20 focus-visible:ring-primary/20"
      />
    </div>
  );
};

export default SearchBar;
