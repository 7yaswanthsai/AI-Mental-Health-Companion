import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import * as SecureStore from "expo-secure-store";

const AuthContext = createContext(null);

const TOKEN_KEY = "pai_mhc_token";
const SUBJECT_KEY = "pai_mhc_subject";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [subjectId, setSubjectId] = useState("S10");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function bootstrap() {
      try {
        const storedToken = await SecureStore.getItemAsync(TOKEN_KEY);
        const storedSubject = await SecureStore.getItemAsync(SUBJECT_KEY);
        if (storedToken) {
          setToken(storedToken);
        }
        if (storedSubject) {
          setSubjectId(storedSubject);
        }
      } finally {
        setLoading(false);
      }
    }
    bootstrap();
  }, []);

  const signIn = async (jwt, subject = "S10") => {
    setToken(jwt);
    setSubjectId(subject);
    await SecureStore.setItemAsync(TOKEN_KEY, jwt);
    await SecureStore.setItemAsync(SUBJECT_KEY, subject);
  };

  const signOut = async () => {
    setToken(null);
    await SecureStore.deleteItemAsync(TOKEN_KEY);
  };

  const value = useMemo(
    () => ({
      token,
      subjectId,
      setSubjectId: async (id) => {
        setSubjectId(id);
        await SecureStore.setItemAsync(SUBJECT_KEY, id);
      },
      signIn,
      signOut,
      loading,
    }),
    [token, subjectId, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}


