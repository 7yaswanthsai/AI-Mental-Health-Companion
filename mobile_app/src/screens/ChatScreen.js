import React, { useCallback, useLayoutEffect, useState, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { createApiClient } from "../api/client";
import { useAuth } from "../context/AuthContext";

function ChatBubble({ item }) {
  const isUser = item.role === "user";
  const timestamp = item.timestamp || "";
  const emotion = item.emotion;

  return (
    <View style={[styles.bubbleContainer, isUser && styles.userBubbleContainer]}>
      <View style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}>
        <Text style={[styles.bubbleText, isUser ? styles.userText : styles.assistantText]}>
          {item.content}
        </Text>
        {timestamp ? (
          <Text style={[styles.timestamp, isUser ? styles.userTimestamp : styles.assistantTimestamp]}>
            {timestamp}
          </Text>
        ) : null}
        {!isUser && emotion && (
          <Text style={styles.emotionTag}>🎭 {emotion}</Text>
        )}
      </View>
    </View>
  );
}

export default function ChatScreen({ navigation }) {
  const { token, signOut, subjectId } = useAuth();
  const [messages, setMessages] = useState([
    {
      id: "intro",
      role: "assistant",
      content: "👋 Hello! I'm your AI mental health companion. How are you feeling today?",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [latestRecommendations, setLatestRecommendations] = useState([]);
  const flatListRef = useRef(null);

  useFocusEffect(
    useCallback(() => {
      if (!token) {
        navigation.replace("Login");
      }
    }, [token, navigation])
  );

  useLayoutEffect(() => {
    navigation.setOptions({
      title: "💬 Chat",
      headerRight: () => (
        <TouchableOpacity
          onPress={() => navigation.navigate("Wellness")}
          style={styles.headerButton}
        >
          <Text style={styles.headerButtonText}>🩺 Wellness</Text>
        </TouchableOpacity>
      ),
    });
  }, [navigation]);

  const handleLogout = async () => {
    Alert.alert("Logout", "Are you sure you want to logout?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Logout",
        style: "destructive",
        onPress: async () => {
          await signOut();
          navigation.replace("Login");
        },
      },
    ]);
  };

  const handleSend = async () => {
    if (!input.trim() || sending) {
      return;
    }

    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    setSending(true);
    try {
      const api = createApiClient(token);
      const response = await api.post("/chat", {
        text: userMessage.content,
        subject_id: subjectId || "S10",
      });

      const { text: botResponse, recommendations, emotion, tone, timestamp } = response.data;

      const assistantMessage = {
        id: `${Date.now()}-bot`,
        role: "assistant",
        content: botResponse || "I'm here for you. Tell me more.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        emotion,
        tone,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setLatestRecommendations(recommendations || []);

      // Scroll to bottom
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    } catch (error) {
      console.error("Chat error", error);
      const errorMessage = {
        id: `${Date.now()}-error`,
        role: "assistant",
        content: "❌ Sorry, I'm having trouble connecting right now. Please try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMessage]);
      Alert.alert("Error", "Unable to reach the assistant right now.");
    } finally {
      setSending(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={90}
    >
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <ChatBubble item={item} />}
        contentContainerStyle={styles.listContent}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {latestRecommendations.length > 0 && (
        <View style={styles.recommendationsContainer}>
          <Text style={styles.recommendationsTitle}>💡 Recommendations</Text>
          <FlatList
            horizontal
            data={latestRecommendations}
            keyExtractor={(item, idx) => `rec-${idx}`}
            renderItem={({ item }) => (
              <View style={styles.recommendationChip}>
                <Text style={styles.recommendationChipText} numberOfLines={2}>
                  {item}
                </Text>
              </View>
            )}
            showsHorizontalScrollIndicator={false}
          />
        </View>
      )}

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Type your message..."
          placeholderTextColor="#9ca3af"
          value={input}
          onChangeText={setInput}
          editable={!sending}
          multiline
          maxLength={500}
        />
        <TouchableOpacity
          style={[styles.sendButton, sending && styles.sendButtonDisabled]}
          onPress={handleSend}
          disabled={sending || !input.trim()}
        >
          {sending ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Text style={styles.sendButtonText}>Send</Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f9fafb",
  },
  listContent: {
    padding: 16,
    paddingBottom: 20,
  },
  bubbleContainer: {
    marginBottom: 12,
    alignItems: "flex-start",
  },
  userBubbleContainer: {
    alignItems: "flex-end",
  },
  bubble: {
    padding: 14,
    borderRadius: 18,
    maxWidth: "75%",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  userBubble: {
    backgroundColor: "#4f46e5",
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    backgroundColor: "#ffffff",
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: "#e5e7eb",
  },
  bubbleText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userText: {
    color: "#ffffff",
  },
  assistantText: {
    color: "#1f2937",
  },
  timestamp: {
    fontSize: 11,
    marginTop: 4,
    opacity: 0.7,
  },
  userTimestamp: {
    color: "#ffffff",
  },
  assistantTimestamp: {
    color: "#6b7280",
  },
  emotionTag: {
    fontSize: 12,
    color: "#6366f1",
    marginTop: 4,
    fontWeight: "500",
  },
  recommendationsContainer: {
    backgroundColor: "#fff3e0",
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderTopWidth: 1,
    borderColor: "#ffe0b2",
  },
  recommendationsTitle: {
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 8,
    color: "#e65100",
  },
  recommendationChip: {
    backgroundColor: "#fff",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    borderWidth: 1,
    borderColor: "#ffcc80",
    maxWidth: 200,
  },
  recommendationChipText: {
    fontSize: 12,
    color: "#e65100",
  },
  inputContainer: {
    flexDirection: "row",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#ffffff",
    borderTopWidth: 1,
    borderColor: "#e5e7eb",
    alignItems: "flex-end",
  },
  input: {
    flex: 1,
    backgroundColor: "#f3f4f6",
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginRight: 8,
    fontSize: 16,
    maxHeight: 100,
    color: "#1f2937",
  },
  sendButton: {
    backgroundColor: "#4f46e5",
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    minWidth: 70,
    alignItems: "center",
    justifyContent: "center",
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  sendButtonText: {
    color: "#ffffff",
    fontWeight: "600",
    fontSize: 16,
  },
  headerButton: {
    marginRight: 8,
  },
  headerButtonText: {
    color: "#4f46e5",
    fontWeight: "600",
    fontSize: 16,
  },
});
