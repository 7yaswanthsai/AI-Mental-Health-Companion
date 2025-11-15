import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Smile, Mic } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import ChatBubble from '@/components/ChatBubble';
import EmotionAvatar from '@/components/EmotionAvatar';
import Navigation from '@/components/Navigation';
import { useStore } from '@/lib/store';
import { chatApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { v4 as uuidv4 } from 'uuid';

const Chat = () => {
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user, messages, addMessage, setMessages } = useStore();
  const { toast } = useToast();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const loadHistory = async () => {
      if (!user.token) return;
      
      try {
        const history = await chatApi.getHistory();
        // Convert history to messages format
        const formattedMessages = (Array.isArray(history) ? history : []).map((msg: any) => ({
          id: uuidv4(),
          role: msg.role || (msg.user_text ? 'user' : 'assistant'),
          content: msg.user_text || msg.bot_response || msg.text || msg.content,
          emotion: msg.emotion || msg.detected_emotion,
          recommendations: msg.recommendations || [],
          timestamp: msg.timestamp || new Date().toISOString(),
        }));
        setMessages(formattedMessages);
      } catch (error) {
        console.error('Failed to load chat history:', error);
      }
    };

    loadHistory();
  }, [user.token]);

  const handleSend = async () => {
    if (!input.trim() || !user.subjectId) return;

    const userMessage = {
      id: uuidv4(),
      role: 'user' as const,
      content: input,
      timestamp: new Date().toISOString(),
    };

    addMessage(userMessage);
    const messageText = input;
    setInput('');
    setIsTyping(true);

    try {
      console.log('Sending message:', messageText, 'to subject:', user.subjectId);
      console.log('API URL:', import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000');
      
      const response = await chatApi.sendMessage(messageText, user.subjectId);
      console.log('Received response:', response);

      const aiMessage = {
        id: uuidv4(),
        role: 'assistant' as const,
        content: response.text,
        emotion: response.emotion,
        emotionProbability: response.probability,
        recommendations: response.recommendations || [],
        timestamp: response.timestamp,
      };

      addMessage(aiMessage);
      
      // Show recommendations toast if available
      if (response.recommendations && response.recommendations.length > 0) {
        toast({
          title: 'Recommendations available',
          description: `Check out ${response.recommendations.length} personalized recommendations`,
        });
      }
      
      // Show crisis alert if escalated
      if (response.escalate) {
        toast({
          title: 'Crisis Support',
          description: 'Please reach out to emergency services if needed',
          variant: 'destructive',
        });
      }
    } catch (error: any) {
      console.error('Chat error details:', {
        message: error.message,
        code: error.code,
        response: error.response?.data,
        status: error.response?.status,
        config: error.config,
      });
      
      let errorMessage = 'Please try again';
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorMessage = 'Request timed out. The server may be processing your message.';
      } else if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
        errorMessage = 'Cannot connect to server. Make sure the backend is running.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast({
        title: 'Failed to send message',
        description: errorMessage,
        variant: 'destructive',
      });
      
      // Add error message to chat for user visibility
      const errorMessageObj = {
        id: uuidv4(),
        role: 'assistant' as const,
        content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date().toISOString(),
      };
      addMessage(errorMessageObj);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="min-h-screen pt-16">
      <Navigation />

      <div className="max-w-5xl mx-auto px-4 py-8 h-[calc(100vh-8rem)] flex flex-col">
        {/* Chat Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-strong rounded-3xl p-6 mb-6"
        >
          <div className="flex items-center gap-4">
            <EmotionAvatar emotion="calm" size="lg" animated={false} />
            <div>
              <h2 className="text-2xl font-bold">Your AI Companion</h2>
              <p className="text-muted-foreground">Always here to listen and support you</p>
            </div>
          </div>
        </motion.div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto mb-6 space-y-4 scroll-smooth">
          <AnimatePresence>
            {messages.map((message) => (
              <ChatBubble
                key={message.id}
                role={message.role}
                content={message.content}
                emotion={message.emotion}
                recommendations={message.recommendations}
                timestamp={message.timestamp}
              />
            ))}
          </AnimatePresence>

          {isTyping && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-3"
            >
              <EmotionAvatar emotion="calm" size="md" />
              <div className="glass rounded-3xl px-6 py-4">
                <div className="flex gap-2">
                  <motion.div
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                    className="w-2 h-2 rounded-full bg-primary"
                  />
                  <motion.div
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                    className="w-2 h-2 rounded-full bg-secondary"
                  />
                  <motion.div
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                    className="w-2 h-2 rounded-full bg-accent"
                  />
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-strong rounded-full p-4"
        >
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full hover-scale"
            >
              <Smile className="w-5 h-5" />
            </Button>

            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Share what's on your mind..."
              className="flex-1 border-0 bg-transparent focus-visible:ring-0 text-base"
            />

            <Button
              variant="ghost"
              size="icon"
              className="rounded-full hover-scale"
            >
              <Mic className="w-5 h-5" />
            </Button>

            <Button
              onClick={handleSend}
              disabled={!input.trim()}
              size="icon"
              className="rounded-full bg-gradient-to-r from-primary to-secondary hover:scale-110 transition-transform"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Chat;
