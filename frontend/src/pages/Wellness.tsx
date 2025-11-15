import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, TrendingUp, Heart, Brain } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import Navigation from '@/components/Navigation';
import GlassCard from '@/components/GlassCard';
import WellnessRadial from '@/components/WellnessRadial';
import { useStore } from '@/lib/store';
import { wellnessApi, WellnessResponse } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

const Wellness = () => {
  const [wellnessData, setWellnessData] = useState<WellnessResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useStore();
  const { toast } = useToast();

  useEffect(() => {
    const fetchWellness = async () => {
      if (!user.subjectId) return;

      try {
        const data = await wellnessApi.getWellness(user.subjectId);
        setWellnessData(data);
      } catch (error: any) {
        toast({
          title: 'Failed to load wellness data',
          description: error.response?.data?.detail || 'Please try again',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchWellness();
  }, [user.subjectId]);

  if (loading) {
    return (
      <div className="min-h-screen pt-16 flex items-center justify-center">
        <Navigation />
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        >
          <Heart className="w-12 h-12 text-primary" />
        </motion.div>
      </div>
    );
  }

  // Map status to emotion for display
  const getEmotionFromStatus = (status: string | undefined): 'calm' | 'stressed' | 'neutral' => {
    if (!status) return 'neutral';
    const statusLower = status.toLowerCase();
    if (statusLower.includes('calm') || statusLower.includes('good')) return 'calm';
    if (statusLower.includes('stress') || statusLower.includes('low')) return 'stressed';
    return 'neutral';
  };

  const emotion = getEmotionFromStatus(wellnessData?.status);

  return (
    <div className="min-h-screen pt-16">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-5xl font-bold mb-4 gradient-text">Wellness Dashboard</h1>
          <p className="text-xl text-muted-foreground">
            Track your mental health journey and insights
          </p>
        </motion.div>

        {/* PWI Score */}
        <div className="grid lg:grid-cols-3 gap-8 mb-8">
          <GlassCard className="lg:col-span-1 flex flex-col items-center justify-center py-12">
            <WellnessRadial value={wellnessData?.pwi || 50} emotion={emotion} />
            {wellnessData?.pwi === null && (
              <p className="mt-4 text-sm text-muted-foreground text-center">
                No wearable data available
              </p>
            )}
          </GlassCard>

          <div className="lg:col-span-2 grid gap-6">
            <GlassCard>
              <div className="flex items-start gap-4">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-calm/20 to-primary/20">
                  <Activity className="w-8 h-8 text-calm" />
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold mb-2">Current State</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {wellnessData?.pwi !== null ? (
                      <>
                        Your wellness state is <span className="font-semibold text-foreground">{wellnessData.status}</span>.
                        {emotion === 'calm' && ' You\'re doing great! Keep up the positive momentum.'}
                        {emotion === 'stressed' && ' Take some time for self-care and relaxation.'}
                        {emotion === 'neutral' && ' You\'re balanced. Consider activities that bring you joy.'}
                      </>
                    ) : (
                      'Wearable data is not available. Connect your device to see wellness metrics.'
                    )}
                  </p>
                </div>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="flex items-start gap-4">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-secondary/20 to-indigo/20">
                  <Brain className="w-8 h-8 text-secondary" />
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold mb-2">Sleep Quality</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {wellnessData?.sleep_quality 
                      ? `Your recent sleep quality is ${wellnessData.sleep_quality}/10`
                      : 'Sleep data will appear here once available'}
                  </p>
                </div>
              </div>
            </GlassCard>
          </div>
        </div>

        {/* Features Display */}
        {wellnessData?.features && Object.keys(wellnessData.features).length > 0 && (
          <GlassCard className="mb-8">
            <h3 className="text-2xl font-bold mb-4">Wellness Features</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(wellnessData.features).map(([key, value]) => (
                <div key={key} className="glass rounded-xl p-4">
                  <p className="text-sm text-muted-foreground uppercase tracking-wider">{key}</p>
                  <p className="text-2xl font-bold mt-2">{typeof value === 'number' ? value.toFixed(2) : value}</p>
                </div>
              ))}
            </div>
          </GlassCard>
        )}

        {/* Trend Chart - Placeholder for future implementation */}
        {false && (
          <GlassCard className="mb-8">
            <div className="flex items-center gap-3 mb-6">
              <TrendingUp className="w-6 h-6 text-primary" />
              <h3 className="text-2xl font-bold">PWI Trend</h3>
            </div>

            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={wellnessData.trend}>
                <XAxis 
                  dataKey="date" 
                  stroke="hsl(var(--muted-foreground))"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  stroke="hsl(var(--muted-foreground))"
                  style={{ fontSize: '12px' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '12px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="pwi"
                  stroke="hsl(var(--primary))"
                  strokeWidth={3}
                  dot={{ fill: 'hsl(var(--primary))', r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </GlassCard>
        )}

        {/* Stress Triggers */}
        {wellnessData?.stress_triggers && wellnessData.stress_triggers.length > 0 && (
          <GlassCard>
            <h3 className="text-2xl font-bold mb-4">Common Stress Triggers</h3>
            <div className="flex flex-wrap gap-3">
              {wellnessData.stress_triggers.map((trigger, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: idx * 0.1 }}
                  className="glass px-4 py-2 rounded-full text-sm font-medium"
                >
                  {trigger}
                </motion.div>
              ))}
            </div>
          </GlassCard>
        )}
      </div>
    </div>
  );
};

export default Wellness;
