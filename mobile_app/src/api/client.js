import axios from "axios";
import Constants from "expo-constants";

const BASE_URL =
  Constants?.expoConfig?.extra?.apiBaseUrl ||
  Constants?.manifest?.extra?.apiBaseUrl ||
  "http://127.0.0.1:8000";

export function createApiClient(token) {
  const instance = axios.create({
    baseURL: BASE_URL,
    timeout: 10000,
  });

  if (token) {
    instance.interceptors.request.use((config) => {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
      return config;
    });
  }

  return instance;
}


