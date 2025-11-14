import axios from "axios";
import Constants from "expo-constants";
import { Platform } from "react-native";

// Get base URL from environment or use platform-specific defaults
function getBaseUrl() {
  // Check for explicit config first (must be a string)
  const configUrl =
    Constants?.expoConfig?.extra?.apiBaseUrl ||
    Constants?.manifest?.extra?.apiBaseUrl;
  
  // Only use configUrl if it's a non-empty string
  if (configUrl && typeof configUrl === "string" && configUrl.trim() !== "") {
    return configUrl.trim();
  }

  // Platform-specific defaults
  if (Platform.OS === "android") {
    // Real device uses laptop's IP
    return "http://10.29.98.165:8000";  
  } else if (Platform.OS === "ios") {
    // iOS simulator can use localhost
    // For physical iOS device, use your computer's local IP
    return __DEV__ ? "http://localhost:8000" : "http://127.0.0.1:8000";
  }
  
  // Web or fallback
  return "http://127.0.0.1:8000";
}

const BASE_URL = getBaseUrl();

// Log the API URL in development for debugging
if (__DEV__) {
  console.log(`[API Client] Using base URL: ${BASE_URL}`);
}

export function createApiClient(token) {
  const instance = axios.create({
    baseURL: BASE_URL,
    timeout: 15000,
    headers: {
      "Content-Type": "application/json",
    },
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

export { BASE_URL };
