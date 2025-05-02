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

/**
 * A simple chat interface for interacting with a task server.
 *
 * The component renders a card with a header, content area, and footer. The
 * content area displays a scrollable list of messages, and the footer contains
 * a text input and a send button.
 *
 * When the user submits a message, the component sends the message to the task
 * server and adds it to the list of messages.
 *
 * The component also displays the current task status, if any, in the content
 * area.
 *
 * The component expects the following props:
 *
 * - `taskId`: The ID of the task to interact with. If not provided, the
 *   component will connect to the task server as a guest.
 */
const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskResponse, setTaskResponse] = useState<TaskResponse | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const client= useRef<WebSocket|null>(null);

  // useEffect(() => {
  //   const ws = new WebSocket(`ws://localhost:1500/ws/${taskId || 'guest'}`);
  //   ws.onmessage = (event) => {
  //     const data = JSON.parse(event.data);
  //     console.log(data);
  //   }
  //   client.current = ws;
  // }, []);
  useEffect(() => {
    // const ws = client.current;
    // if (!ws) return;

    const ws = new WebSocket(`ws://localhost:1500/ws/${taskId || 'guest'}`);
    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'request_session' }));
    };

    ws.onmessage = (event) => {
      
      const data = JSON.parse(event.data);
      console.log(event)
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
    return () => ws.close();
  }, [taskId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  /**
   * Handles the submission of a message by the user.
   *
   * When the user submits a message, the component adds the message to the list
   * of messages and resets the input field.
   *
   * @param {React.FormEvent} e The form event.
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages(prev => [...prev, {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }]);

    client.current?.send(input);
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
