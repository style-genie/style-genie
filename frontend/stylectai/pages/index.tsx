import Image from "next/image";
import { Geist, Geist_Mono } from "next/font/google";
import { useState } from "react";
import { Style } from "@/lib/types";
import UserForm from "@/components/user-form";
import TitlebarImageList from "@/pages/ImageList";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function Home() {
  const [recommendedStyles, setRecommendedStyles] = useState<Style[]>([]);

  function handleRecommendations(data) {
    setRecommendedStyles(data);
  }
  return (
    <div
      className={`${geistSans.className} ${geistMono.className} flex flex-col min-h-screen font-[family-name:var(--font-geist-sans)]`}
    >
     <div className="flex-1 w-full py-10 px-4 bg-gray-100">
        <div className="container mx-auto">
          <h1 className="text-3xl font-black font-bold mb-6 text-center">
            Style Recommendations
          </h1>

          <UserForm 
            id="recommendation-form"
            returnRecommendations ={handleRecommendations}
            className="mb-10"
          />

          {recommendedStyles.length > 0 ? (
            <TitlebarImageList recommendations={recommendedStyles}></TitlebarImageList>
          ) : (
            <div className="w-full flex justify-center h-60 pt-10"></div>
          )}
        </div>
      </div>
      <footer className="w-full py-4 flex gap-[24px] flex-wrap items-center justify-center bg-white">
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=default-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/file.svg"
            alt="File icon"
            width={16}
            height={16}
          />
          Git
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=default-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/window.svg"
            alt="Window icon"
            width={16}
            height={16}
          />
          Made with ❤️ by&nbsp;StyleGenie team.
        </a>
      </footer>
    </div>
  );
}
