import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send } from 'lucide-react';
import { Menu, Settings } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
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
  role: 'system' | 'user' | 'history';
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
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskResponse, setTaskResponse] = useState<TaskResponse | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const client = useRef<WebSocket | null>(null);
  const [userFilter, setUserFilter] = useState('');
  const [outfits, setOutfits] = useState(false);
  const [shoes, setShoes] = useState(false);
  const [trousers, setTrousers] = useState(false);
  const [jackets, setJackets] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:1500/ws/${taskId || 'guest'}`);

    client.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(event);
      setMessages(prev => [...prev, {
        role: 'system',
        content: data.message,
        timestamp: new Date().toISOString()
      }]);
      if (data.task_id) {
        setTaskId(data.task_id);
      } else if (data.messages) {
        setMessages(prev => [...prev, {
          role: 'system',
          content: data.message,
          timestamp: new Date().toISOString()
        }]);
      } else if (data.achievements) {
        setTaskResponse(data);
      }
    };

  }, [taskId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
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
          </CardHeader>
          <CardContent className="flex-grow flex flex-col w-full h-full">
            <ScrollArea className="flex-grow w-10 h-full" ref={scrollRef}>
              <div className="space-y-2 w-full">
                {messages.map((msg, index) => (
                  <div
                    key={`\${msg.timestamp}-\${index}`}
                    className={`text-\${msg.role === 'user' ? 'right' : 'left'}`}
                  >
                    <div
                      className={`inline-block p-3 rounded-lg max-w-[80%] \${msg.role === 'user'
                        ? 'bg-blue-500 text-white rounded-br-sm'
                        : 'bg-gray-200 rounded-bl-sm'
                        }`}
                    >
                      {msg.content}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
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

            <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
             <div className="w-[280%]"> <Input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Enter your message..."
                className="flex-1"
              />
              </div>
              
              <Button type="submit"  class="w-[10%] flex items-center justify-center rounded-2xl">
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
                <ScrollArea className="h-full">
                  <div className="flex flex-row gap-2">
                    <Button onClick={() => setOutfits(!outfits)} className={`h-8 p-1 text-sm ${outfits ? 'bg-sky-500 text-white' : ''}`}>
                      Outfits: {outfits ? 'On' : 'Off'}
                    </Button>
                    <Button onClick={() => setShoes(!shoes)} className={`h-8 p-1 text-sm ${shoes ? 'bg-sky-500 text-white' : ''}`}>
                      Shoes: {shoes ? 'On' : 'Off'}
                    </Button>
                    <Button onClick={() => setTrousers(!trousers)} className={`h-8 p-1 text-sm ${trousers ? 'bg-sky-500 text-white' : ''}`}>
                      Trousers: {trousers ? 'On' : 'Off'}
                    </Button>
                    <Button onClick={() => setJackets(!jackets)} className={`h-8 p-1 text-sm ${jackets ? 'bg-sky-500 text-white' : ''}`}>
                      Jackets: {jackets ? 'On' : 'Off'}
                    </Button>
                  </div>
                </ScrollArea>
              </TabsContent>
              <TabsContent value="userdata" className="h-full">
                <ScrollArea className="h-full">
                  <div>User Data Content</div>
                </ScrollArea>
              </TabsContent>
              <TabsContent value="searchresults" className="h-full">
                <ScrollArea className="h-full">
                  <div>Search Results Content</div>
                </ScrollArea>
              </TabsContent>
              <TabsContent value="searchcontext" className="h-full">
                <ScrollArea className="h-full">
                  <div>Search Context Content</div>
                </ScrollArea>
              </TabsContent>
              <TabsContent value="virtualtryon" className="h-full">
                <ScrollArea className="h-full">
                  <div>Virtual Tryon Content</div>
                </ScrollArea>
              </TabsContent>
              <TabsContent value="plan" className="h-full">
                <ScrollArea className="h-full">
                  <div>Plan Content</div>
                </ScrollArea>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ChatInterface;
