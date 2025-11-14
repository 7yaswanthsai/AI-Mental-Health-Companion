import React, { useEffect, useState, useLayoutEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  ActivityIndicator,
  Alert,
  ScrollView,
  TouchableOpacity,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { createApiClient } from "../api/client";
import { useAuth } from "../context/AuthContext";

function RecommendationCard({ item, index }) {
  return (
    <View style={styles.recommendationCard}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardNumber}>{index + 1}</Text>
        <View style={styles.cardContent}>
          <Text style={styles.cardText}>{item.text}</Text>
          {item.emotion && (
            <Text style={styles.cardEmotion}>🎭 {item.emotion}</Text>
          )}
          {item.timestamp && (
            <Text style={styles.cardTimestamp}>{item.timestamp}</Text>
          )}
        </View>
      </View>
    </View>
  );
}

export default function RecommendationsScreen({ navigation }) {
  const { token, subjectId } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const fetchRecommendations = async (emotion, wellnessStatus) => {
    if (!emotion) {
      Alert.alert("Info", "Send a chat message first to get recommendations.");
      return;
    }

    setLoading(true);
    try {
      const api = createApiClient(token);
      const response = await api.get("/recommendations", {
        params: {
          emotion: emotion,
          wellness_status: wellnessStatus || null,
        },
      });

      const recs = response.data?.recommendations || [];
      const recItems = recs.map((text, idx) => ({
        id: `${Date.now()}-${idx}`,
        text,
        emotion,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      }));

      setRecommendations(recItems);
      setHistory((prev) => [
        ...recItems.map((r) => ({ ...r, id: `${r.id}-hist` })),
        ...prev,
      ].slice(0, 20));
    } catch (error) {
      console.error("Recommendations fetch failed", error);
      Alert.alert("Error", "Unable to fetch recommendations. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    React.useCallback(() => {
      if (!token) {
        navigation.replace("Login");
        return;
      }
    }, [token])
  );

  useLayoutEffect(() => {
    navigation.setOptions({
      title: "💡 Recommendations",
      headerRight: () => (
        <TouchableOpacity
          onPress={() => {
            Alert.alert(
              "Get Recommendations",
              "Enter an emotion to get personalized recommendations:",
              [
                { text: "Cancel", style: "cancel" },
                {
                  text: "Sadness",
                  onPress: () => fetchRecommendations("sadness", null),
                },
                {
                  text: "Anxiety",
                  onPress: () => fetchRecommendations("anxiety", null),
                },
                {
                  text: "Joy",
                  onPress: () => fetchRecommendations("joy", null),
                },
                {
                  text: "Anger",
                  onPress: () => fetchRecommendations("anger", null),
                },
              ]
            );
          }}
          style={{ marginRight: 8 }}
        >
          <Text style={{ color: "#4f46e5", fontWeight: "600" }}>🔄</Text>
        </TouchableOpacity>
      ),
    });
  }, [navigation]);

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl
          refreshing={loading}
          onRefresh={() => fetchRecommendations("neutral", null)}
        />
      }
    >
      {recommendations.length > 0 ? (
        <>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Current Recommendations</Text>
            {recommendations.map((item, index) => (
              <RecommendationCard key={item.id} item={item} index={index} />
            ))}
          </View>

          {history.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Recommendation History</Text>
              <FlatList
                data={history}
                keyExtractor={(item) => item.id}
                scrollEnabled={false}
                renderItem={({ item, index }) => (
                  <RecommendationCard item={item} index={index} />
                )}
              />
            </View>
          )}
        </>
      ) : (
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateIcon}>💡</Text>
          <Text style={styles.emptyStateText}>
            No recommendations yet
          </Text>
          <Text style={styles.emptyStateSubtext}>
            Send a chat message or use the refresh button to get personalized
            recommendations based on your emotions and wellness status.
          </Text>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate("Chat")}
          >
            <Text style={styles.actionButtonText}>Go to Chat</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f9fafb",
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "600",
    color: "#1f2937",
    marginBottom: 16,
  },
  recommendationCard: {
    backgroundColor: "#ffffff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    borderLeftWidth: 4,
    borderLeftColor: "#ff9800",
  },
  cardHeader: {
    flexDirection: "row",
  },
  cardNumber: {
    fontSize: 24,
    fontWeight: "700",
    color: "#ff9800",
    marginRight: 12,
    minWidth: 30,
  },
  cardContent: {
    flex: 1,
  },
  cardText: {
    fontSize: 16,
    lineHeight: 22,
    color: "#1f2937",
    marginBottom: 8,
  },
  cardEmotion: {
    fontSize: 12,
    color: "#6366f1",
    fontWeight: "500",
    marginBottom: 4,
  },
  cardTimestamp: {
    fontSize: 11,
    color: "#9ca3af",
  },
  emptyState: {
    alignItems: "center",
    justifyContent: "center",
    padding: 48,
    marginTop: 100,
  },
  emptyStateIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyStateText: {
    fontSize: 20,
    fontWeight: "600",
    color: "#1f2937",
    marginBottom: 8,
    textAlign: "center",
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: "#6b7280",
    textAlign: "center",
    marginBottom: 24,
    lineHeight: 20,
  },
  actionButton: {
    backgroundColor: "#4f46e5",
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  actionButtonText: {
    color: "#ffffff",
    fontWeight: "600",
    fontSize: 16,
  },
});

