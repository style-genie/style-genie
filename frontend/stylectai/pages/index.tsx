import Image from "next/image";
import { Geist, Geist_Mono } from "next/font/google";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Style } from "@/lib/types";
import UserForm from "@/components/user-form";

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
            className="mb-10"
          />

          {recommendedStyles.length > 0 ? (
            <>
              <h2 className="text-2xl font-bold mb-4 text-center">
                Recommended Styles
              </h2>
              <div
                id="recommended-books"
                className="flex overflow-x-scroll pb-10 hide-scroll-bar"
              >
                <section className="container mx-auto mb-12">
                  <div className="flex flex-wrap -mx-2">
                    {recommendedStyles.map((style: Style) => {
                      return (
                        <div key={style.index} className="w-full md:w-1/3 px-2 mb-4 animate-pop-in">
                          <div className="bg-white p-6 flex items-center flex-col">
                            <div className='flex justify-between w-full'>
                              <h3 className="text-xl font-semibold mb-4 line-clamp-1">{style.title}</h3>
                            </div>
                            <div className='w-48 h-72'>
                              <img
                                src={style.thumbnail}
                                alt={"Thumbnail of the style " + style.title}
                                className="w-full h-full rounded-lg shadow-lg"
                              />
                            </div>
       
                            <div className='flex'>
                              <Button className="bg-black text-white w-full rounded-md hover:bg-gray-800 hover:text-white" type="submit" variant="outline" onClick={() => { }}>
                                Try on
                              </Button>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </section>
              </div>
            </>
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
