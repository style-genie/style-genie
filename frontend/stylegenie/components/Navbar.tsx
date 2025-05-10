
import { Search } from "lucide-react";
import Logo from "./ui/logo";
import { Button } from "./ui/button";
import { Input } from "./ui/input";

const Navbar = () => {
  return (
    <nav className="border-border py-4 px-6 bg-white/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-12">
          <Logo />
          
          <div className="hidden md:flex items-center space-x-8">
            <a href="/" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              Home
            </a>
            <a href="/categories" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              Categories
            </a>
            <a href="/profile" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              Profile
            </a>
          </div>
        </div>
        
        <div className="relative w-full max-w-xs hidden md:block">
          <Input 
            type="search" 
            placeholder="Search..." 
            className="pr-10 bg-secondary/50 border-0 focus:ring-primary/20 focus-visible:ring-primary/20" 
          />
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        </div>
        
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" className="md:hidden">
            <Search className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="sm" className="hidden md:inline-flex">
            Sign In
          </Button>
          <Button size="sm" className="hidden md:inline-flex">
            Sign Up
          </Button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
