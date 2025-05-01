import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send } from 'lucide-react';

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

  // WebSocket-Verbindung herstellen
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${taskId || 'guest'}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.task_id) {
        setTaskId(data.task_id);
      } else if (data.messages) {
        setMessages(data.messages);
      } else if (data.achievements) {
        setTaskResponse(data);
      }
    };
    return () => ws.close();
  }, [taskId]);

  // Automatisches Scrollen zum letzten Nachrichten
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages(prev => [...prev, {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }]);
    setInput('');
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Task Interface</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] mb-4" ref={scrollRef}>
          {messages.map((msg, index) => (
            <div
              key={`${msg.timestamp}-${index}`}
              className={`mb-4 ${
                msg.role === 'user' ? 'text-right' : 'text-left'
              }`}
            >
              <div
                className={`p-3 rounded-lg max-w-[80%] ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-br-sm'
                    : 'bg-muted rounded-bl-sm'
                }`}
              >
                {msg.content}
              </div>
              <div className="text-xs text-muted-foreground">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </ScrollArea>

        {taskResponse && (
          <div className="space-y-4 mb-4">
            <h3 className="text-lg font-semibold">Task Status</h3>
            <div className="space-y-2">
              <p><strong>Achievements:</strong> {taskResponse.achievements.join(', ')}</p>
              <p><strong>Next Steps:</strong> {taskResponse.next_steps}</p>
              <p><strong>Feedback Required:</strong> {taskResponse.user_feedback_required ? 'Yes' : 'No'}</p>
              <p><strong>Tools Required:</strong> {taskResponse.tools_required_next.join(', ')}</p>
              <p><strong>Important Notes:</strong> {taskResponse.important_notes}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter your message..."
            className="flex-1"
          />
          <Button type="submit">
            <Send className="h-4 w-4 mr-2" />
            Send
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default ChatInterface;