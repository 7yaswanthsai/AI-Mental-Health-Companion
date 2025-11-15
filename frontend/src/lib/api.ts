import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('pai-mhc-token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
    data: config.data,
    headers: { ...config.headers, Authorization: token ? 'Bearer ***' : 'None' },
  });
  return config;
});

// Log responses and errors
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response from ${response.config.url}:`, response.status, response.data);
    return response;
  },
  (error) => {
    console.error(`[API] Error from ${error.config?.url}:`, {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      data: error.response?.data,
    });
    return Promise.reject(error);
  }
);

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface ChatRequest {
  text: string;
  subject_id?: string;
}

export interface ChatResponse {
  text: string;
  emotion: string;
  probability: number;
  wellness: {
    subject_id: string;
    pwi: number | null;
    status: string;
    features?: Record<string, number>;
  };
  recommendations: string[];
  timestamp: string;
  tags: string[];
  tone?: string;
  escalate: boolean;
}

export interface WellnessResponse {
  subject_id: string;
  pwi: number | null;
  status: string;
  features?: Record<string, number>;
}

export const authApi = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/login', {
      email,
      password,
    });
    return response.data;
  },
};

export const chatApi = {
  sendMessage: async (text: string, subjectId?: string): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat', {
      text,
      subject_id: subjectId,
    });
    return response.data;
  },

  getHistory: async () => {
    const response = await api.get('/history');
    return response.data;
  },
};

export const wellnessApi = {
  getWellness: async (subjectId: string): Promise<WellnessResponse> => {
    const response = await api.get<WellnessResponse>(`/wellness/${subjectId}`);
    return response.data;
  },

  getRecommendations: async (emotion: string, wellnessStatus?: string) => {
    const params = new URLSearchParams({ emotion });
    if (wellnessStatus) {
      params.append('wellness_status', wellnessStatus);
    }
    const response = await api.get(`/recommendations?${params.toString()}`);
    return response.data;
  },
};

export default api;
