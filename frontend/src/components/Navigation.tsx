import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Heart, MessageCircle, Activity, Lightbulb, LogOut } from 'lucide-react';
import { useStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const Navigation = () => {
  const location = useLocation();
  const { user, clearUser } = useStore();

  const navItems = [
    { path: '/chat', label: 'Chat', icon: MessageCircle },
    { path: '/wellness', label: 'Wellness', icon: Activity },
    { path: '/recommendations', label: 'Recommendations', icon: Lightbulb },
  ];

  if (!user.token) return null;

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed top-0 left-0 right-0 z-50 glass-strong border-b border-white/20"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <Heart className="w-6 h-6 text-primary" />
            <span className="font-bold text-xl gradient-text">PAI-MHC</span>
          </Link>

          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;

              return (
                <Link key={item.path} to={item.path}>
                  <Button
                    variant="ghost"
                    className={cn(
                      'relative transition-all duration-300',
                      isActive && 'text-primary font-semibold'
                    )}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.label}
                    {isActive && (
                      <motion.div
                        layoutId="activeTab"
                        className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
                        transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                      />
                    )}
                  </Button>
                </Link>
              );
            })}

            <Button
              variant="ghost"
              onClick={clearUser}
              className="ml-4 text-muted-foreground hover:text-destructive"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navigation;
