import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface GradientButtonProps {
  children: ReactNode;
  onClick?: () => void;
  className?: string;
  variant?: 'primary' | 'secondary';
  type?: 'button' | 'submit';
}

const GradientButton = ({
  children,
  onClick,
  className,
  variant = 'primary',
  type = 'button',
}: GradientButtonProps) => {
  const variants = {
    primary: 'bg-gradient-to-r from-primary via-secondary to-accent text-white',
    secondary: 'glass text-foreground border-2 border-primary/30',
  };

  return (
    <motion.button
      type={type}
      whileHover={{ scale: 1.05, boxShadow: '0 0 30px hsl(174, 72%, 56% / 0.5)' }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={cn(
        'px-8 py-4 rounded-full font-semibold text-lg transition-all duration-300',
        variants[variant],
        className
      )}
    >
      {children}
    </motion.button>
  );
};

export default GradientButton;
