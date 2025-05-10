
import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useToast } from "@/hooks/use-toast";
import LogoAlt from "./ui/logo-alt";

const Newsletter = () => {
  const [email, setEmail] = useState("");
  const { toast } = useToast();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (email) {
      toast({
        title: "Successfully subscribed!",
        description: "Thank you for subscribing to our newsletter.",
      });
      setEmail("");
    }
  };
  
  return (
    <div className="bg-primary text-white py-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="md:w-1/3">
            <div className="mb-4 flex justify-center md:justify-start">
              <div className="bg-white rounded-full p-2">
                <LogoAlt />
              </div>
            </div>
            <h3 className="text-2xl font-playfair font-medium mb-2 text-center md:text-left">Subscribe to our newsletter</h3>
            <p className="text-white/80 text-center md:text-left">Get the latest updates on trends and exclusive offers</p>
          </div>
          
          <form onSubmit={handleSubmit} className="w-full md:w-2/3 max-w-lg">
            <div className="flex gap-2">
              <Input
                type="email"
                placeholder="Your email address"
                className="newsletter-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Button type="submit" variant="secondary" className="shrink-0">
                Subscribe
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Newsletter;
