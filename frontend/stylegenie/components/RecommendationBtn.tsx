
import { Button } from "./ui/button";
import { Sparkles } from "lucide-react";

interface RecommendButtonProps {
  onClick: () => void;
}

const RecommendButton = ({ onClick }: RecommendButtonProps) => {
  return (
    <div className="w-full max-w-xl mx-auto mb-4 text-center">
      <Button 
        onClick={onClick} 
        className="px-6 py-2 text-sm font-medium shadow-sm hover:shadow-md transition-all bg-primary hover:bg-primary/90"
      >
        <Sparkles className="h-4 w-4 mr-2" />
        Discover Styles
      </Button>
    </div>
  );
};

export default RecommendButton;
