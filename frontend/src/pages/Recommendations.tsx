import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lightbulb, ChevronDown, Wind, BookOpen, Brain, Heart } from 'lucide-react';
import Navigation from '@/components/Navigation';
import GlassCard from '@/components/GlassCard';
import { useStore } from '@/lib/store';
import { wellnessApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useStore();
  const { toast } = useToast();

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!user.subjectId) {
        setLoading(false);
        return;
      }

      try {
        // Get wellness status first
        const wellnessData = await wellnessApi.getWellness(user.subjectId);
        
        // Get recommendations based on current emotion/wellness
        // For now, use a default emotion - in real app, get from latest chat
        const data = await wellnessApi.getRecommendations('neutral', wellnessData.status);
        
        // Convert API response to display format
        if (data.recommendations && Array.isArray(data.recommendations)) {
          const formattedRecs = data.recommendations.map((rec: string, idx: number) => ({
            id: idx + 1,
            title: rec,
            icon: Lightbulb,
            category: 'Personalized Recommendation',
            description: rec,
            steps: [rec],
          }));
          setRecommendations(formattedRecs);
        }
      } catch (error: any) {
        toast({
          title: 'Failed to load recommendations',
          description: error.response?.data?.detail || 'Please try again',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [user.subjectId]);

  const defaultRecommendations = [
    {
      id: 1,
      title: '5-4-3-2-1 Grounding Technique',
      icon: Wind,
      category: 'Anxiety Relief',
      description: 'A powerful mindfulness exercise to bring you back to the present moment.',
      steps: [
        'Name 5 things you can see around you',
        'Name 4 things you can touch',
        'Name 3 things you can hear',
        'Name 2 things you can smell',
        'Name 1 thing you can taste',
      ],
    },
    {
      id: 2,
      title: 'Box Breathing',
      icon: Heart,
      category: 'Stress Management',
      description: 'A simple breathing technique used by Navy SEALs to stay calm.',
      steps: [
        'Breathe in for 4 seconds',
        'Hold your breath for 4 seconds',
        'Breathe out for 4 seconds',
        'Hold for 4 seconds',
        'Repeat 4-5 times',
      ],
    },
    {
      id: 3,
      title: '3-Minute Journaling',
      icon: BookOpen,
      category: 'Self-Reflection',
      description: 'Quick journaling prompts to process your thoughts and emotions.',
      steps: [
        'What am I grateful for today?',
        'What\'s one thing that made me smile?',
        'What\'s one challenge I faced?',
        'How did I handle it?',
        'What can I improve tomorrow?',
      ],
    },
    {
      id: 4,
      title: 'Cognitive Reframing',
      icon: Brain,
      category: 'Thought Patterns',
      description: 'Transform negative thoughts into constructive perspectives.',
      steps: [
        'Identify the negative thought',
        'Challenge: Is this thought factual?',
        'Find evidence for and against',
        'Create a balanced alternative',
        'Practice the new perspective',
      ],
    },
  ];

  const displayRecommendations = recommendations.length > 0 ? recommendations : defaultRecommendations;

  if (loading) {
    return (
      <div className="min-h-screen pt-16 flex items-center justify-center">
        <Navigation />
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        >
          <Lightbulb className="w-12 h-12 text-primary" />
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-16">
      <Navigation />

      <div className="max-w-5xl mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-5xl font-bold mb-4 gradient-text">Personalized Recommendations</h1>
          <p className="text-xl text-muted-foreground">
            Evidence-based techniques tailored to support your wellbeing
          </p>
        </motion.div>

        <div className="space-y-6">
          {displayRecommendations.map((rec, idx) => {
            const Icon = rec.icon || Lightbulb;
            const isExpanded = expandedId === rec.id;

            return (
              <motion.div
                key={rec.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <GlassCard
                  hover={false}
                  className="cursor-pointer"
                  onClick={() => setExpandedId(isExpanded ? null : rec.id)}
                >
                  <div className="flex items-start gap-4">
                    <div className="p-4 rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 flex-shrink-0">
                      <Icon className="w-6 h-6 text-primary" />
                    </div>

                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                            {rec.category}
                          </span>
                          <h3 className="text-2xl font-bold mt-1">{rec.title}</h3>
                          <p className="text-muted-foreground mt-2">{rec.description}</p>
                        </div>

                        <motion.div
                          animate={{ rotate: isExpanded ? 180 : 0 }}
                          transition={{ duration: 0.3 }}
                        >
                          <ChevronDown className="w-6 h-6 text-muted-foreground" />
                        </motion.div>
                      </div>

                      <AnimatePresence>
                        {isExpanded && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.3 }}
                            className="overflow-hidden"
                          >
                            <div className="mt-6 pt-6 border-t border-white/20">
                              <h4 className="font-semibold mb-4">Steps to follow:</h4>
                              <ol className="space-y-3">
                                {rec.steps?.map((step: string, stepIdx: number) => (
                                  <motion.li
                                    key={stepIdx}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: stepIdx * 0.1 }}
                                    className="flex gap-3"
                                  >
                                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center text-sm font-semibold">
                                      {stepIdx + 1}
                                    </span>
                                    <span className="text-muted-foreground leading-relaxed">
                                      {step}
                                    </span>
                                  </motion.li>
                                ))}
                              </ol>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Recommendations;
