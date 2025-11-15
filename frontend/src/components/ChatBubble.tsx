import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import EmotionAvatar from './EmotionAvatar';
import { Badge } from '@/components/ui/badge';

interface ChatBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  emotion?: string;
  recommendations?: string[];
  timestamp?: string;
}

const ChatBubble = ({ role, content, emotion, recommendations, timestamp }: ChatBubbleProps) => {
  const isUser = role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={cn('flex gap-3 mb-4', isUser && 'flex-row-reverse')}
    >
      {!isUser && <EmotionAvatar emotion={emotion} size="md" />}

      <div className={cn('flex flex-col gap-2 max-w-[70%]', isUser && 'items-end')}>
        <div
          className={cn(
            'rounded-3xl px-6 py-4 shadow-md',
            isUser
              ? 'bg-gradient-to-r from-primary to-secondary text-white'
              : 'glass text-foreground'
          )}
        >
          <p className="text-base leading-relaxed">{content}</p>
        </div>

        {recommendations && recommendations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="flex flex-wrap gap-2 mt-2"
          >
            {recommendations.map((rec, idx) => (
              <Badge
                key={idx}
                variant="secondary"
                className="cursor-pointer hover:scale-105 transition-transform"
              >
                {rec}
              </Badge>
            ))}
          </motion.div>
        )}

        {timestamp && (
          <span className="text-xs text-muted-foreground px-2">
            {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        )}
      </div>
    </motion.div>
  );
};

export default ChatBubble;
