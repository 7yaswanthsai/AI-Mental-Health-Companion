import { motion } from 'framer-motion';
import { Smile, Meh, Frown, Sparkles } from 'lucide-react';

interface EmotionAvatarProps {
  emotion?: string;
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
  intensity?: number;
}

const EmotionAvatar = ({ 
  emotion = 'neutral', 
  size = 'md', 
  animated = true,
  intensity = 0.7 
}: EmotionAvatarProps) => {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  const getEmotionConfig = () => {
    const emotionLower = emotion.toLowerCase();
    
    if (emotionLower.includes('happy') || emotionLower.includes('joy')) {
      return {
        Icon: Smile,
        color: 'text-happy',
        bgColor: 'bg-happy/20',
        glowColor: 'shadow-[0_0_20px_hsl(45,97%,59%/0.4)]',
        animation: 'animate-bounce',
      };
    }
    
    if (emotionLower.includes('calm')) {
      return {
        Icon: Smile,
        color: 'text-calm',
        bgColor: 'bg-calm/20',
        glowColor: 'shadow-[0_0_20px_hsl(174,72%,56%/0.4)]',
        animation: 'breathing',
      };
    }
    
    if (emotionLower.includes('stress') || emotionLower.includes('anxious')) {
      return {
        Icon: Frown,
        color: 'text-stressed',
        bgColor: 'bg-stressed/20',
        glowColor: 'shadow-[0_0_20px_hsl(0,84%,60%/0.4)]',
        animation: 'animate-pulse',
      };
    }
    
    if (emotionLower.includes('sad')) {
      return {
        Icon: Frown,
        color: 'text-sad',
        bgColor: 'bg-sad/20',
        glowColor: 'shadow-[0_0_20px_hsl(221,83%,69%/0.4)]',
        animation: '',
      };
    }
    
    return {
      Icon: Meh,
      color: 'text-neutral',
      bgColor: 'bg-neutral/20',
      glowColor: 'shadow-[0_0_20px_hsl(263,70%,70%/0.4)]',
      animation: 'breathing',
    };
  };

  const { Icon, color, bgColor, glowColor, animation } = getEmotionConfig();
  const showHappy = emotion.toLowerCase().includes('happy');

  return (
    <motion.div
      initial={animated ? { scale: 0 } : undefined}
      animate={animated ? { scale: 1 } : undefined}
      className={`${sizes[size]} ${bgColor} ${glowColor} rounded-full flex items-center justify-center relative ${animated ? animation : ''}`}
      style={{
        transition: 'all 0.3s ease-in-out',
      }}
    >
      <Icon className={`${size === 'sm' ? 'w-4 h-4' : size === 'md' ? 'w-6 h-6' : 'w-8 h-8'} ${color}`} />
      
      {showHappy && animated && (
        <>
          <motion.div
            className="absolute"
            initial={{ scale: 0, rotate: 0 }}
            animate={{ scale: [0, 1, 0], rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, delay: 0 }}
          >
            <Sparkles className="w-3 h-3 text-happy absolute -top-2 -right-2" />
          </motion.div>
          <motion.div
            className="absolute"
            initial={{ scale: 0, rotate: 0 }}
            animate={{ scale: [0, 1, 0], rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, delay: 0.5 }}
          >
            <Sparkles className="w-3 h-3 text-happy absolute -bottom-2 -left-2" />
          </motion.div>
        </>
      )}
    </motion.div>
  );
};

export default EmotionAvatar;
