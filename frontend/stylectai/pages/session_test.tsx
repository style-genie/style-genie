import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from "@/components/ui/textarea"

import { Button } from "@/components/ui/button"

import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Minus } from 'lucide-react';
import { Menu, Settings } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import dynamic from 'next/dynamic';

import { deleteCookie } from 'cookies-next';
import { useRouter } from 'next/router';
import { Button as Button2 } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface Message {
  role: 'system' | 'user' | 'history' | 'agent' | 'agent_meta';
  content: string;
  timestamp: string;
}
interface TaskResponse {
  achievements: string[];
  next_steps: string;
  user_feedback_required: boolean;
  markdown_media_portal: string;
  tools_required_next: string[];
  important_notes: string;
  task_finished: boolean;
  step_failed: boolean;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState('thinking');
  const [agentMessage, setAgentMessage] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskResponse, setTaskResponse] = useState<TaskResponse | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const client = useRef<WebSocket | null>(null);
  const [userFilter, setUserFilter] = useState('');
  const [userInfo, setUserInfo] = useState('');
  const [userImages, setUserImages] = useState('');
  const [userStyle, setUserStyle] = useState('');
  const [userPrompt, setuserPrompt] = useState('');
  const [outfits, setOutfits] = useState(true);
  const [shoes, setShoes] = useState(true);
  const [trousers, setTrousers] = useState(true);
  const [shirts, setShirts] = useState(true);
  const [jackets, setJackets] = useState(true);
  const [bags, setBags] = useState(true);
  const [accessories, setAccessories] = useState(true);
  const [hats, setHats] = useState(true);
  const [skirts, setSkirts] = useState(true);
  const [coats, setCoats] = useState(true);
  const [userInfoFilter, setuserInfoFilter] = useState(true);
  const [userImagesFilter, setuserImagesFilter] = useState(true);
  const [userStyleFilter, setuserStyleFilter] = useState(true);
  const [userPromptFilter, setuserPromptFilter] = useState(true);
  const [userModifiersFilter, setserModifiersFilter] = useState(true);

  const [imageLinks, setImageLinks] = useState<string[]>(["https://image.vip.de/23271306/t/3a/v2/w960/r0/-/leonardo-di-caprio-t2580-jpg--topic-image-2580-.jpg"]);
  const [newImageLink, setNewImageLink] = useState('');
  const [userModifiers, setUserModifiers] = useState({
    sexy:0,
    casual:0,
    formal:0,
    sporty:0,
    trendy:0,
    party:0,
    vintage:0,
    elegant:0,
    minimal:0,
    bohemian:0,
    romantic:0,
    chic:0,
  });
  const registry = {
    outfits: { setter: setOutfits, accessor: outfits },
    shoes: { setter: setShoes, accessor: shoes },
    trousers: { setter: setTrousers, accessor: trousers },
    shirts: { setter: setShirts, accessor: shirts },
    jackets: { setter: setJackets, accessor: jackets },
    bags: { setter: setBags, accessor: bags },
    accessories: { setter: setAccessories, accessor: accessories },
    hats: { setter: setHats, accessor: hats },
    skirts: { setter: setSkirts, accessor: skirts },
    userInfoFilter: { setter: setuserInfoFilter, accessor: userInfoFilter },
    userImagesFilter: { setter: setuserImagesFilter, accessor: userImagesFilter },
    userStyleFilter: { setter: setuserStyleFilter, accessor: userStyleFilter },
    userPromptFilter: { setter: setuserPromptFilter, accessor: userPromptFilter },
    userModifiersFilter: { setter: setserModifiersFilter, accessor: userModifiersFilter },
  };

 const  icons={
trousers: <img src= 'https://www.svgrepo.com/show/37413/masculine-trouser-outline.svg ' alt="TrousersIcon"></img>,
shirts: <img src='https://www.svgrepo.com/show/425793/shirt.svg ' alt="ShirtIcon"></img>,
jackets: <img src='https://www.svgrepo.com/show/425788/jacket.svg' alt="JacketIcon"></img>,
skirts: <img src='https://www.svgrepo.com/show/482436/skirt-1.svg' alt="SkirtIcon"></img>,
//dresses: <img src='https://www.svgrepo.com/show/482584/dress-4.svg' alt="HatIcon"></img>,
shoes: <img src= 'https://www.svgrepo.com/show/482539/shoe-5.svg' alt="ShoeIcon"></img>,
//CoatIcon: <img src='https://www.svgrepo.com/show/317083/coat.svg' alt="CoatIcon"></img>,
//TopIcon: <img src='https://www.svgrepo.com/show/416027/blouse-cami-camisole-2.svg' alt="TopIcon"></img>,
hats: <img src='https://www.svgrepo.com/show/487438/hat.svg' alt="Hat2Icon"></img>,
bags: <img src='https://www.svgrepo.com/show/482502/bag-2.svg' alt="bagIcon"></img>,
accessories: <img src='https://www.svgrepo.com/show/513131/glasses.svg' alt="accessoriesIcon"></img>,
outfits: <img src='https://www.svgrepo.com/show/285453/suit.svg' alt="accessoriesIcon"></img>,
userImages: <img src='https://www.svgrepo.com/show/473267/image.svg' alt="accessoriesIcon"></img>,
userStyle:  <img src='https://www.svgrepo.com/show/424748/style-emoji-smiley.svg' alt="accessoriesIcon"></img>,
userPrompt:  <img src='https://www.svgrepo.com/show/494485/talk-talk.svg' alt="accessoriesIcon"></img>,
userInfo: <img src='https://www.svgrepo.com/show/458241/info-alt.svg' alt="accessoriesIcon"></img>,
userModifiers :<img src='https://www.svgrepo.com/show/471876/settings-04.svg' alt="accessoriesIcon"></img>,


}
  const updateState = (stateName: string, value: any) => {
    const state = registry[stateName];
    if (state && state.setter) {
      state.setter(value);
    } else {
      console.warn(`State ${stateName} not found in registry.`);
    }
  };
  function updateUserSettings(){
    const obj={
      "sexyModifier":userModifiers.sexy,
      "casualModifier":userModifiers.casual,
      "formalModifier":userModifiers.formal,
      "sportyModifier":userModifiers.sporty,
      "trendyModifier":userModifiers.trendy,
      "partyModifier":userModifiers.party,
      "vintageModifier":userModifiers.vintage,
      "elegantModifier":userModifiers.elegant,
      "minimalModifier":userModifiers.minimal,
      "bohemianModifier":userModifiers.bohemian,
      "romanticModifier":userModifiers.romantic,
      "chicFilter":userModifiers.chic,
      "outfitsFilter":outfits,
      "shoesFilter":shoes,
      "trousersFilter":trousers,
      "shirtsFilter":shirts,
      "jacketsFilter":jackets,
      "bagsFilter":bags,
      "accessoriesFilter":accessories,
      "hatsFilter":hats,
      "skirtsFilter":skirts,
      "userInfoFilter":userInfoFilter,
      "userImagesFilter":userImagesFilter,
      "userStyleFilter":userStyleFilter,
      "userPromptFilter":userPromptFilter,
      "userModifiersFilter":userModifiersFilter,
      "userInfo":userInfo,
      "userImages":userImages,
      "userStyle":userStyle,
    }
  }

  // eg outfits -> shoes -> hash-value -> {image:https://...,description:"...",link:"https://..."}
  function set(id: string, value: string, field = "") {
    // if(field!="" && id!="" && value!=""){
    //   registry[id](value);
    // }
    // else{
    //   registry[id](value);
    // }
  }

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:1500/ws/${taskId || 'guest'}`);

    client.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      const message = data.message.response
      console.log("Received data:", message);
      const method  = data.method_response
      console.log("Received method:", method);

      if(method=="request"){
        setStatus('request');
        
        setMessages(prev => [...prev, {
          role: 'agent_meta',
          content: 'Agent is thinking...',
          timestamp: new Date().toISOString(),
        },
        {
        role: 'agent',
        content: message || "No response received",
        timestamp: new Date().toISOString(),
        
      }]);
      console.log("Updated messages:", messages);
      }
      // if (data.task_id) {
      //   setTaskId(data.task_id);
      // } else if (data.messages) {
      //   setMessages(prev => [...prev, {
      //     role: 'system',
      //     content: data.message.response,
      //     timestamp: new Date().toISOString()
      //   }]);
      // } else if (data.achievements) {
      //   setTaskResponse(data);
      // }
    };

  }, [taskId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
    console.log("Updated messages:", messages);
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    client.current?.send(input);
    setMessages(prev => [...prev, {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }]);

    setInput('');
  };

  const handleUserFilterChange = (filter: string) => {
    setUserFilter(filter);
    console.log(`Filtering users by: ${filter}`);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Chat Window */}
      <div className="w-1/2 p-8 relative">
        <Card className="h-full flex flex-col relative">
          <CardHeader>
            <CardTitle>Task Interface</CardTitle>
            <div>Status: {status}</div>
          </CardHeader>
          <CardContent className="flex-grow flex flex-col w-full h-full">
            <ScrollArea className="flex-grow w-full text-black h-full flex items-center content-center" ref={scrollRef}>
              <div className="space-y-2 w-[80%]">
                {messages.map((msg, index) => (
                  <div
                    key={crypto.randomUUID()}
                    className={`text-\${msg.role === 'agent' ? 'right' : 'left'}`}
                  >
                    <div
                      className={`inline-block p-3 rounded-lg w-full    ${msg.role === 'agent_meta'
                        ? 'bg-blue-100 text-xs h-[50%]  text-green-600 rounded-br-sm '
                        : 'bg-white text-black rounded-bl-sm'
                        }}`}
                    >
                      {msg.content}
                      {msg.role === 'agent' && (
                    <div className="text-xs text-gray-500">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </div>
                  )}
                    </div>
                    </div>
                    ))
                  }
            </div>
                                  
            </ScrollArea>

            {taskResponse && (
              <div className="mt-4 space-y-2">
                <h3 className="text-lg font-semibold">Task Status</h3>
                <div>
                  <p>
                    <strong>Achievements:</strong> {taskResponse.achievements.join(', ')}
                  </p>
                  <p>
                    <strong>Next Steps:</strong> {taskResponse.next_steps}
                  </p>
                  <p>
                    <strong>Feedback Required:</strong> {taskResponse.user_feedback_required ? 'Yes' : 'No'}
                  </p>
                  <p>
                    <strong>Tools Required:</strong> {taskResponse.tools_required_next.join(', ')}
                  </p>
                  <p>
                    <strong>Important Notes:</strong> {taskResponse.important_notes}
                  </p>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-4 flex gap-2 items-center justify-center">
              <div className="w-[280%]"> <Input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Enter your message..."
                className="flex-1"
              />
              </div>

              <Button type="submit" className="w-[10%] flex items-center justify-center rounded-2xl">
                <Send className="h-full " />

              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      {/* User Info and Tools Window */}
      <div className="w-1/2 p-8">
        <Card className="h-full flex flex-col">
          <CardHeader>
            <CardTitle>User Info & Tools</CardTitle>
          </CardHeader>
          <CardContent className="flex-grow flex flex-col">
            <div className="absolute top-2 right-2 z-10 flex flex-col">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button2 variant="ghost" className="w-4 h-4 p-2 rounded-md">
                    <Settings className="h-4 w-4" />
                    <span className="sr-only">Open menu</span>
                  </Button2>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-[200px] bg-amber-300 rounded-md">
                  <DropdownMenuLabel>Account</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <div>Key: [user key]</div>
                    <div>Username: [username]</div>
                    <div>Time: [time]</div>
                    <div>Location: [location]</div>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>Settings</DropdownMenuItem>
                  <DropdownMenuItem>Logout</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
             
            </div>
            <Tabs defaultValue="preferences" className="w-full h-full">
              <TabsList className="flex flex-row gap-2 items-center justify-center">
                <TabsTrigger value="preferences" className="data-[state=active]:bg-blue-500 data-[state=active]:text-white">Preferences</TabsTrigger>
                <TabsTrigger value="userdata" className="data-[state=active]:bg-blue-500 data-[state=active]:text-white">User Data</TabsTrigger>
                <TabsTrigger value="searchresults" className="data-[state=active]:bg-blue-500 data-[state=active]:text-white">Search Results</TabsTrigger>
                <TabsTrigger value="searchcontext" className="data-[state=active]:bg-blue-500 data-[state=active]:text-white">Search Context</TabsTrigger>
                <TabsTrigger value="virtualtryon" className="data-[state=active]:bg-blue-500 data-[state=active]:text-white">Virtual Tryon</TabsTrigger>
                <TabsTrigger value="plan" className="data-[state=active]:bg-blue-500 data-[state=active]:text-white">Plan</TabsTrigger>
              </TabsList>
              <TabsContent value="preferences" className="h-full">
                <div className='w-full h-full flex-row gap-2 items-center justify-center'>
                <ScrollArea className=" ">
                  <div className="grid grid-cols-4 gap-2">
                    {
                      Object.entries(registry).map(([key, value]: [string, object]) => (
                        <Button 
                          key={key}
                          onClick={() => updateState(key, !registry[key].accessor)}
                           variant="outline"
                          className={`filter-button flex flex-row items-center justify-center h-8 p-2 text-sm ${registry[key].accessor ? 'bg-sky-500 text-white' : ''}`}
                        >
                          <div className='w-[80%] text-xs'>{key}</div> 
                           {/* {value.accessor ? 'ON' : 'OFF'} */}
                          <div className="w-[20%] ml-1">{icons[key]}</div>
                        </Button>
                      ))
                      }
                  </div>
                </ScrollArea>
                <Input
                      type="text"
                      placeholder="User Input Prompt"
                      value={userPrompt}
                      onChange={(e) => updateState('userPrompt', e.target.value)}
                    />
                <ScrollArea className="h-[20%]">
                  
                  {Object.entries(userModifiers).map(([key, value]: [string, number]) => (
                    <div key={key} className="flex flex-col gap-2">
                      <label className="text-xs">{key}</label>
                      <input
                        type="range"
                        className='w-0.5 h-2.5 '
                        min="0"
                        max="100"
                        value={userModifiers[key]}
                        onChange={(e) => updateState('userModifiers', {...userModifiers, [key]: parseInt(e.target.value)})}
                      />
                    </div>
                  ))}
                 
                </ScrollArea>
                <div className='h-[5%] pt-2 flex justify-center items-center'>
                  <Button className='h-[60%] w-[50%]'  onClick={updateUserSettings}>Submit</Button>
                </div> 
                </div>
              </TabsContent>
              <TabsContent value="userdata" className="h-full">
                <div className="h-full w-full flex-row gap-2 items-center justify-center">
                <div className="h-[90%] w-full flex-row gap-2 items-center justify-center">
                <div className="flex flex-col flex flex-col gap-2">
              <div  className="h-[40%]  rounded-md">
                <ScrollArea className='h-full'>
                    <div className="mt-4 grid grid-cols-4 gap-2 h-full">
                      {imageLinks.map((link, index) => (
                        <div key={index} className="relative">
                          <img src={link} alt={`User Image ${index}`} className="w-32 h-32 object-cover" />
                          <Button
                            onClick={() => {
                              const newImageLinks = [...imageLinks];
                              newImageLinks.splice(index, 1);
                              setImageLinks(newImageLinks);
                            }}
                            className="absolute top-0 right-0 p-0.5 h-4 bg-gray-200 rounded-full hover:bg-gray-300"
                          >
                            <Minus className="w-3 h-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                    
                </ScrollArea>
                <div className="flex gap-2 align-start h-full justify-start items-center justify-center">
                      <Input
                        type="text"
                        placeholder="Image Link"
                        value={newImageLink}
                        onChange={(e) => setNewImageLink(e.target.value)}
                      />
                      <Button onClick={() => {
                        setImageLinks([...imageLinks, newImageLink]);
                        setNewImageLink('');
                      }}>Add</Button>
                    </div>
                  </div>
                  
                  
                <div className='h-[30%] w-full '>
                <ScrollArea className="h-full ">
                  <h1>About Me</h1>
                  <Textarea
                    className='resize-none h-[80px]'
                    type="text"
                    placeholder="about me"
                    value={userInfo}
                    onChange={(e) => updateState('userInfo', e.target.value)}
                  />
                </ScrollArea>
                </div>
                <ScrollArea className="h-full">
                  <h2>My Style</h2>
                  <Textarea
                    type="text"
                    className='resize-none h-[70px]'
                    placeholder="My Style"
                    value={userStyle}
                    onChange={(e) => updateState('userStyle', e.target.value)}
                  />
                </ScrollArea>
                </div>
                </div><div>
                </div> 
                <div className='h-[10%] pt-2 flex justify-center items-center'>
                  <Button className='h-[60%] w-[50%]' onClick={updateUserSettings}>Submit</Button>
                </div> 
                </div>
              </TabsContent>
              <TabsContent value="searchresults" className="h-full">
              </TabsContent>
              <TabsContent value="searchcontext" className="h-full">
                <ScrollArea className="h-full"></ScrollArea>
              </TabsContent>
              <TabsContent value="virtualtryon" className="h-full">
                <ScrollArea className="h-full"></ScrollArea>
              </TabsContent>
              <TabsContent value="plan" className="h-full">
                <ScrollArea className="h-full"></ScrollArea>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

<style jsx>{`
  div {
    position: fixed;
    bottom: 0;
    width: 100%;
  }
`}</style>

export default ChatInterface;
