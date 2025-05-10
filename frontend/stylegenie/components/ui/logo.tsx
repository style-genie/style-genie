import { Star } from "lucide-react";
import Image from "next/image";

const Logo = () => {
  return (
    <a href="/" className="flex items-center space-x-2 group">
         <Image
            src="/logo.png"
            alt="Logo"
            width={210}
            height={40}
          />
      {/* <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-white shadow-md group-hover:rotate-12 transition-transform">
        <Star className="h-5 w-5" />
      </div>
      <span className="font-playfair text-xl font-semibold text-primary group-hover:text-primary/80 transition-colors">
        Style<span className="font-semibold">Genic</span>
      </span> */}
    </a>
  );
};

export default Logo;
