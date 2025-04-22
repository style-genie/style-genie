
import { useCallback, useEffect, useState } from "react";

import {useDropzone} from 'react-dropzone'

import { PlusIcon } from "@/components/icons/plus-icon";


import Image from 'next/image'

import Compress from "compress.js"


function getDefaultValue(attachment:string[]|null){
    if(!attachment) return null;
    return Array.isArray(attachment) ? attachment:[attachment];
}

interface UploaderProps {
    onChange:any;
    value:any;
    name:string;
    onBlur:any;
    multiple:boolean;
    maxSize?:number;
    isLoading?:boolean;
}

export default function Uploader({
    onChange,
    value,
    name,
    onBlur,
    multiple,
    isLoading,
    maxSize
}:UploaderProps){
    let [attechments,setAttachments]= useState<string[]|null>(
        getDefaultValue(value)
    );

    const compressor = new Compress();


   

    // const { mutate,isLoading,isSuccess} =useMutation(client.users.updatePicture,{
    //     onSuccess:(response)=>{
    //         const data = multiple ? response:response[0];
    //         //console.log("the data photo",data,typeof data)
          
    //         onChange(data);
    //         setAttachments(getDefaultValue([data]))
    //         //setAttachments(response)
    //     },
    //     onError:(error)=>{
    //         console.log(error,"upload avatar error")
    //     }
    // });

    useEffect(()=>{
        setAttachments(getDefaultValue(value))
    },[value])

    // !!! under construction: to extract the function to lib.
    const compres= async (acceptedFiles:any) => {

        const file = acceptedFiles[0];       
        const newFile = await compressor.compress(file, {
          quality: 0.8,
          crop: true, // If true, will crop a square image from the center.
          maxWidth: 230, // Image width will not exceed 320px.
          maxHeight: 230, // Image height will not exceed 320px.
        });  
        return newFile
        
    } 


    const onDrop =useCallback(
        async (acceptedFiles:any)=>{
            try{const imageCompres = await compres(acceptedFiles)

       
        }catch(error){
             console.error("Error compressing image:", error);
        }}
      ,[])

      const { getRootProps, getInputProps } = useDropzone({
        //@ts-ignore
        accept: 'image/*',
        multiple,
        onDrop
    
      });

      //maxsize: !!! under construction : add a size checker.
      //maxSize




 // !!! under constuction: for now just one image not multiple images.
    return (

    <div className="flex flex-wrap gap-2.5">
        <div
           {...getRootProps({
            className: 
                'relative border-dashed border-2 border-light-500 dark:border-dark-600 text-center flex flex-col justify-center hover:text-black dark:hover:text-light items-center cursor-pointer focus:border-accent-400 focus:outline-none h-36 w-full rounded',
                // {
                //   'h-20 w-20 rounded-md shrink-0': multiple === true,
                //   'h-36 w-full rounded': multiple === false,
                // }
             
            })}
       >
        <input 
            {...getInputProps({
                name,
                onBlur
            })}
        />
        {
    
                Array.isArray(attechments)
                ? attechments.map((at,index)=>(
                    <div key={index}>
                       <div className="relative h-20 w-20 overflow-hidden rounded-full">
                         <Image
                            alt="Avatar"
                            src={at}
                            fill
                            //loading="lazy"
                            className="object-scale-down"
                          />
                        </div>
                    
                    </div>
                )) : 'Upload Your Dream Style Image (80 X 80)'
                }
                {isLoading && (
                    <span className="mt-2.5 flex items-center gap-1 font-medium text-light-500">
                        <PlusIcon className="h-4 w-4 animate-spin" />
                        Uploading...
                      
                    </span>
                )}
       </div>
    </div>
    )
}