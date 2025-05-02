import { object, string } from "yup";
import { Form } from "./ui/form"
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { StyleInput } from "@/lib/types";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { twMerge } from "tailwind-merge";
import { Controller } from "react-hook-form";
import Uploader from "./image-uploader";



const  UserForm =({id,className, returnRecommendations}:{id:string,className:string, returnRecommendations: any})=>{

  const [query, setQuery] = useState('');
  const [image,setImage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  // const {me} = useUserStore((state)=>({
  //   me: state.me,
  // }));

  const onSubmit = (data: StyleInput) => {
    console.log(data);
    returnRecommendations(data)
  };

  const styleValidationSchema = object({
    prompt: string().required('Your prompt is required'),
    emailAddress: string().email('Invalid email address').required('Email is required'),
    image: string().required('Your image is required'),

  });


return (
   <>
      <Form
            onSubmit={onSubmit}
            validationSchema={styleValidationSchema}
            id={id}
            className={twMerge(cn("flex flex-grow flex-col", className))}
                >
           {({ register, reset, setValue,control, formState: { errors } }) => (
            <>
             <div className="mb-4">
                <label
                    htmlFor="favorite-styles"
                    className="block text-gray-700 font-bold mb-2"
                  >
                  What would you like to get a style recommendation on?
                </label>
                  <Input
                    type="text"
                    id="favorite-books"
                    name="favorite-books"
                    placeholder="I'd like to learn..."
                    className="block w-full px-4 py-2 border border-gray-300 bg-white rounded-md shadow-sm "
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value);
                    }}
                  />
                    <Controller
                        name="image"
                        control={control}
                        render={({ field: { ref, ...rest } }) => (
                                    <div className="sm:col-span-2 mt-4">
                                        {/* <span className="block cursor-pointer pb-2.5 font-normal text-dark/70 dark:text-light/70"> */}
                                        <label
                                             htmlFor="favorite-styles"
                                         className="block text-gray-700 font-bold mb-2"
                                             >
                                            Your style image
                                        </label>
                                        <div className="text-xs">
                                           <Uploader {...rest} isLoading={isLoading} multiple={false} value={image} />
                                      </div>
                                    </div>
                                    )}
                    />

              </div>
                  <Button className="bg-black text-white w-full rounded-md hover:bg-gray-800 hover:text-white" disabled={isLoading} type="submit" variant="outline">
                  Get Recommendations
                  </Button>
               </>
                   )}

       </Form>

   </>
   )

}

export default UserForm
