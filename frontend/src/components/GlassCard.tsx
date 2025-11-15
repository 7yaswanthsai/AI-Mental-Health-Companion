import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  delay?: number;
  onClick?: () => void;
}

const GlassCard = ({ children, className, hover = true, delay = 0, onClick }: GlassCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay }}
      whileHover={hover ? { scale: 1.02, y: -5 } : undefined}
      onClick={onClick}
      className={cn(
        'glass rounded-3xl p-6 shadow-lg transition-all duration-300',
        hover && 'hover-glow cursor-pointer',
        className
      )}
    >
      {children}
    </motion.div>
  );
};

export default GlassCard;
