import React, { useCallback, useLayoutEffect, useState } from "react";
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, ActivityIndicator, Alert } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { createApiClient } from "../api/client";
import { useAuth } from "../context/AuthContext";

function ChatBubble({ item }) {
  const isUser = item.role === "user";
  return (
    <View style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}>
      <Text style={[styles.bubbleText, isUser ? styles.userText : styles.assistantText]}>{item.content}</Text>
    </View>
  );
}

export default function ChatScreen({ navigation }) {
  const { token, signOut, subjectId } = useAuth();
  const [messages, setMessages] = useState([
    { id: "intro", role: "assistant", content: "👋 Hello! I’m your AI mental health companion. How are you feeling today?" },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [latestRecommendations, setLatestRecommendations] = useState([]);

  useFocusEffect(
    useCallback(() => {
      if (!token) {
        navigation.replace("Login");
      }
    }, [token, navigation])
  );

  useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <TouchableOpacity onPress={() => navigation.navigate("Wellness")}>
          <Text style={{ color: "#2563eb", fontWeight: "600" }}>Wellness</Text>
        </TouchableOpacity>
      ),
    });
  }, [navigation]);

  const handleLogout = async () => {
    await signOut();
    navigation.replace("Login");
  };

  const handleSend = async () => {
    if (!input.trim()) {
      return;
    }
    const userMessage = { id: Date.now().toString(), role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    setSending(true);
    try {
      const api = createApiClient(token);
      const response = await api.post("/chat", {
        text: userMessage.content,
        subject_id: subjectId,
      });
      const { text: botResponse, recommendations, timestamp } = response.data;
      const assistantMessage = {
        id: `${Date.now()}-bot`,
        role: "assistant",
        content: botResponse || "I'm here for you. Tell me more.",
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setLatestRecommendations(recommendations || []);
    } catch (error) {
      console.error("Chat error", error);
      Alert.alert("Error", "Unable to reach the assistant right now.");
    } finally {
      setSending(false);
    }
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={ChatBubble}
        contentContainerStyle={styles.listContent}
      />
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Type your message..."
          value={input}
          onChangeText={setInput}
          editable={!sending}
        />
        <TouchableOpacity style={styles.sendButton} onPress={handleSend} disabled={sending}>
          {sending ? <ActivityIndicator color="#fff" /> : <Text style={styles.sendButtonText}>Send</Text>}
        </TouchableOpacity>
      </View>
      {latestRecommendations.length > 0 && (
        <View style={styles.recommendationsContainer}>
          <Text style={styles.recommendationsTitle}>Recommendations</Text>
          {latestRecommendations.map((rec, idx) => (
            <Text key={idx} style={styles.recommendationItem}>
              • {rec}
            </Text>
          ))}
        </View>
      )}
      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>Log out</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f7f7ff",
  },
  listContent: {
    padding: 16,
    paddingBottom: 120,
  },
  bubble: {
    padding: 14,
    borderRadius: 16,
    marginBottom: 12,
    maxWidth: "80%",
  },
  userBubble: {
    backgroundColor: "#4f46e5",
    alignSelf: "flex-end",
  },
  assistantBubble: {
    backgroundColor: "#e0e7ff",
    alignSelf: "flex-start",
  },
  bubbleText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userText: {
    color: "#fff",
  },
  assistantText: {
    color: "#1f2937",
  },
  inputContainer: {
    flexDirection: "row",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#fff",
    borderTopWidth: 1,
    borderColor: "#e5e7eb",
    alignItems: "center",
  },
  input: {
    flex: 1,
    backgroundColor: "#f3f4f6",
    borderRadius: 999,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginRight: 12,
    fontSize: 16,
  },
  sendButton: {
    backgroundColor: "#4f46e5",
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 999,
  },
  sendButtonText: {
    color: "#fff",
    fontWeight: "600",
  },
  recommendationsContainer: {
    backgroundColor: "#fff",
    padding: 16,
    borderTopWidth: 1,
    borderColor: "#e5e7eb",
  },
  recommendationsTitle: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 8,
  },
  recommendationItem: {
    fontSize: 14,
    color: "#374151",
    marginBottom: 4,
  },
  logoutButton: {
    alignSelf: "center",
    marginVertical: 16,
  },
  logoutText: {
    color: "#ef4444",
    fontWeight: "600",
  },
});

