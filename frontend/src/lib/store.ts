import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  emotion?: string;
  emotionProbability?: number;
  recommendations?: string[];
  timestamp: string;
}

export interface WellnessData {
  pwi: number;
  emotion: 'calm' | 'stressed' | 'neutral';
  sleepQuality?: number;
  stressTriggers?: string[];
  emotionHistory?: Array<{ date: string; emotion: string }>;
}

interface AppState {
  user: {
    id: string | null;
    token: string | null;
    subjectId: string | null;
  };
  messages: Message[];
  wellnessData: WellnessData | null;
  setUser: (id: string, token: string, subjectId: string) => void;
  clearUser: () => void;
  addMessage: (message: Message) => void;
  setMessages: (messages: Message[]) => void;
  setWellnessData: (data: WellnessData) => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      user: {
        id: null,
        token: null,
        subjectId: null,
      },
      messages: [],
      wellnessData: null,
      setUser: (id, token, subjectId) =>
        set({ user: { id, token, subjectId } }),
      clearUser: () =>
        set({ user: { id: null, token: null, subjectId: null }, messages: [], wellnessData: null }),
      addMessage: (message) =>
        set((state) => ({ messages: [...state.messages, message] })),
      setMessages: (messages) => set({ messages }),
      setWellnessData: (data) => set({ wellnessData: data }),
    }),
    {
      name: 'pai-mhc-storage',
    }
  )
);
