import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface WellnessRadialProps {
  value: number;
  emotion: 'calm' | 'stressed' | 'neutral';
}

const WellnessRadial = ({ value, emotion }: WellnessRadialProps) => {
  const circumference = 2 * Math.PI * 90;
  const offset = circumference - (value / 100) * circumference;

  const emotionConfig = {
    calm: {
      color: 'text-calm',
      strokeColor: 'hsl(142, 76%, 56%)',
      glowClass: 'shadow-[0_0_40px_hsl(142,76%,56%/0.5)]',
    },
    stressed: {
      color: 'text-stressed',
      strokeColor: 'hsl(0, 84%, 60%)',
      glowClass: 'shadow-[0_0_40px_hsl(0,84%,60%/0.5)]',
    },
    neutral: {
      color: 'text-neutral',
      strokeColor: 'hsl(220, 15%, 80%)',
      glowClass: 'shadow-[0_0_40px_hsl(220,15%,80%/0.3)]',
    },
  };

  const config = emotionConfig[emotion];

  return (
    <div className="relative flex items-center justify-center">
      <svg className="w-64 h-64 transform -rotate-90">
        {/* Background circle */}
        <circle
          cx="128"
          cy="128"
          r="90"
          stroke="hsl(220, 20%, 88%)"
          strokeWidth="12"
          fill="none"
        />
        {/* Progress circle */}
        <motion.circle
          cx="128"
          cy="128"
          r="90"
          stroke={config.strokeColor}
          strokeWidth="12"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: 'easeInOut' }}
          className={cn('breathing', config.glowClass)}
        />
      </svg>

      <div className="absolute flex flex-col items-center">
        <motion.span
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.5, type: 'spring' }}
          className={cn('text-6xl font-bold', config.color)}
        >
          {value}
        </motion.span>
        <span className="text-sm text-muted-foreground mt-2">PWI Score</span>
        <span className={cn('text-xs font-semibold mt-1 uppercase', config.color)}>
          {emotion}
        </span>
      </div>
    </div>
  );
};

export default WellnessRadial;
