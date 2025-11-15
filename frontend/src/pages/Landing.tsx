import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Heart, Brain, Shield, Sparkles } from 'lucide-react';
import FloatingOrb from '@/components/FloatingOrb';
import GlassCard from '@/components/GlassCard';
import GradientButton from '@/components/GradientButton';
import { useStore } from '@/lib/store';

const Landing = () => {
  const navigate = useNavigate();
  const { user } = useStore();

  const features = [
    {
      icon: Heart,
      title: 'AI Emotional Support',
      description: 'Compassionate conversations powered by advanced AI that truly understands your feelings.',
    },
    {
      icon: Brain,
      title: 'Wearable-Aware Wellness',
      description: 'Integrated insights from your health data to provide personalized mental health guidance.',
    },
    {
      icon: Sparkles,
      title: 'Personalized Therapy',
      description: 'Tailored recommendations and therapeutic techniques designed just for you.',
    },
    {
      icon: Shield,
      title: 'Private & Secure',
      description: 'Your conversations and data are end-to-end encrypted and completely confidential.',
    },
  ];

  const handleGetStarted = () => {
    if (user.token) {
      navigate('/chat');
    } else {
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-4 overflow-hidden">
        {/* Floating particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 rounded-full bg-primary/30"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                y: [0, -30, 0],
                opacity: [0.2, 0.5, 0.2],
              }}
              transition={{
                duration: 3 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center z-10 max-w-4xl"
        >
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mb-8"
          >
            <Heart className="w-20 h-20 mx-auto text-primary breathing" />
          </motion.div>

          <h1 className="text-6xl md:text-7xl font-bold mb-6 gradient-text">
            Your space to talk, heal, and feel understood
          </h1>

          <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-2xl mx-auto">
            PAI-MHC blends AI empathy with wellness intelligence to support you anytime, anywhere.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <GradientButton onClick={handleGetStarted}>
              Start Using the App
            </GradientButton>
            <GradientButton variant="secondary" onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}>
              Learn More
            </GradientButton>
          </div>
        </motion.div>

        {/* 3D Orb */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 1 }}
          className="w-full max-w-2xl"
        >
          <FloatingOrb />
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-bold mb-4 gradient-text">
              Designed for Your Wellbeing
            </h2>
            <p className="text-xl text-muted-foreground">
              Experience mental health support that feels natural, caring, and truly personal.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8">
            {features.map((feature, idx) => (
              <GlassCard key={idx} delay={idx * 0.1}>
                <div className="flex items-start gap-4">
                  <div className="p-4 rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20">
                    <feature.icon className="w-8 h-8 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold mb-2">{feature.title}</h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto text-center"
        >
          <GlassCard hover={false} className="p-12">
            <h2 className="text-4xl font-bold mb-6 gradient-text">
              Ready to begin your journey?
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Take the first step towards better mental health today.
            </p>
            <GradientButton onClick={handleGetStarted}>
              Get Started Now
            </GradientButton>
          </GlassCard>
        </motion.div>
      </section>
    </div>
  );
};

export default Landing;
