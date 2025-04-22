import * as React from 'react';

import {Style} from "@/lib/types";
import {Button} from "@/components/ui/button";

export default function TitlebarImageList(props) {
  return (
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
                    {props.recommendations.map((style: Style) => {
                      return (
                        <div key={style.index} className="w-full md:w-1/3 animate-pop-in">
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
                              <Button className="bg-black text-white w-full rounded-md hover:bg-gray-800 hover:text-white" type="submit"
                                      variant="outline" onClick={() => { }}>
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
  )
}