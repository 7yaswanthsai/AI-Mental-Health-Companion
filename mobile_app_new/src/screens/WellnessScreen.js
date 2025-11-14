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
  Dimensions,
  TouchableOpacity,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { createApiClient } from "../api/client";
import { useAuth } from "../context/AuthContext";

const { width } = Dimensions.get("window");

// Simple line chart component
function SimpleLineChart({ data }) {
  if (!data || data.length < 2) {
    return (
      <View style={styles.chartPlaceholder}>
        <Text style={styles.chartPlaceholderText}>Need at least 2 data points</Text>
      </View>
    );
  }

  const maxValue = Math.max(...data.map((d) => d.pwi || 0));
  const minValue = Math.min(...data.map((d) => d.pwi || 0));
  const range = maxValue - minValue || 1;
  const chartHeight = 150;
  const chartWidth = width - 64;
  const pointSpacing = chartWidth / (data.length - 1);

  const points = data.map((item, index) => ({
    x: index * pointSpacing,
    y: chartHeight - ((item.pwi - minValue) / range) * chartHeight,
    value: item.pwi,
  }));

  return (
    <View style={styles.chartContainer}>
      <View style={styles.chart}>
        <View style={styles.chartAxis}>
          <Text style={styles.chartAxisLabel}>{maxValue.toFixed(0)}</Text>
          <Text style={styles.chartAxisLabel}>{minValue.toFixed(0)}</Text>
        </View>
        <View style={styles.chartLineContainer}>
          {points.map((point, idx) => (
            <React.Fragment key={idx}>
              {idx > 0 && (
                <View
                  style={[
                    styles.chartLine,
                    {
                      left: points[idx - 1].x,
                      top: points[idx - 1].y,
                      width: Math.sqrt(
                        Math.pow(point.x - points[idx - 1].x, 2) +
                          Math.pow(point.y - points[idx - 1].y, 2)
                      ),
                      transform: [
                        {
                          rotate: `${Math.atan2(
                            point.y - points[idx - 1].y,
                            point.x - points[idx - 1].x
                          )}rad`,
                        },
                      ],
                    },
                  ]}
                />
              )}
              <View
                style={[
                  styles.chartPoint,
                  {
                    left: point.x - 4,
                    top: point.y - 4,
                  },
                ]}
              />
            </React.Fragment>
          ))}
        </View>
      </View>
    </View>
  );
}

function StatusBadge({ status }) {
  const statusColors = {
    Calm: { bg: "#d1fae5", text: "#065f46", border: "#10b981" },
    Neutral: { bg: "#dbeafe", text: "#1e40af", border: "#3b82f6" },
    "Mild Stress": { bg: "#fed7aa", text: "#9a3412", border: "#f97316" },
    Stressed: { bg: "#fee2e2", text: "#991b1b", border: "#ef4444" },
    "High Stress": { bg: "#fecaca", text: "#7f1d1d", border: "#dc2626" },
  };

  const colors = statusColors[status] || { bg: "#f3f4f6", text: "#374151", border: "#9ca3af" };

  return (
    <View style={[styles.statusBadge, { backgroundColor: colors.bg, borderColor: colors.border }]}>
      <Text style={[styles.statusBadgeText, { color: colors.text }]}>{status || "Unknown"}</Text>
    </View>
  );
}

export default function WellnessScreen({ navigation }) {
  const { token, subjectId } = useAuth();
  const [currentSnapshot, setCurrentSnapshot] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchWellness = async () => {
    setLoading(true);
    try {
      const api = createApiClient(token);
      const response = await api.get(`/wellness/${subjectId || "S10"}`);
      const snapshot = response.data;

      if (snapshot && snapshot.pwi !== null && snapshot.pwi !== undefined) {
        setCurrentSnapshot(snapshot);
        setHistory((prev) => {
          const newHistory = [
            {
              id: Date.now().toString(),
              ...snapshot,
              timestamp: new Date().toLocaleString(),
            },
            ...prev,
          ];
          return newHistory.slice(0, 20); // Keep last 20
        });
      } else {
        Alert.alert("No Data", "Wellness data not available for this subject.");
      }
    } catch (error) {
      console.error("Wellness fetch failed", error);
      Alert.alert("Error", "Unable to fetch wellness data. Please try again.");
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
      fetchWellness();
    }, [token, subjectId])
  );

  useLayoutEffect(() => {
    navigation.setOptions({
      title: "🩺 Wellness Dashboard",
      headerRight: () => (
        <TouchableOpacity onPress={fetchWellness} style={{ marginRight: 8 }}>
          <Text style={{ color: "#4f46e5", fontWeight: "600" }}>🔄</Text>
        </TouchableOpacity>
      ),
    });
  }, [navigation]);

  const getPwiColor = (pwi) => {
    if (pwi >= 70) return "#10b981"; // Green
    if (pwi >= 40) return "#3b82f6"; // Blue
    if (pwi >= 30) return "#f97316"; // Orange
    return "#ef4444"; // Red
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={loading} onRefresh={fetchWellness} />}
    >
      {currentSnapshot && currentSnapshot.pwi !== null ? (
        <>
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Current PWI Score</Text>
            <Text
              style={[
                styles.cardValue,
                { color: getPwiColor(currentSnapshot.pwi) },
              ]}
            >
              {currentSnapshot.pwi.toFixed(1)}
            </Text>
            <StatusBadge status={currentSnapshot.status} />
            {currentSnapshot.timestamp && (
              <Text style={styles.cardTimestamp}>
                Last updated: {new Date(currentSnapshot.timestamp).toLocaleString()}
              </Text>
            )}
          </View>

          {history.length > 1 && (
            <View style={styles.chartCard}>
              <Text style={styles.sectionTitle}>📈 Wellness Trend</Text>
              <SimpleLineChart data={history.slice().reverse()} />
            </View>
          )}

          <View style={styles.featuresCard}>
            <Text style={styles.sectionTitle}>📊 Features</Text>
            {currentSnapshot.features && (
              <View style={styles.featuresGrid}>
                {Object.entries(currentSnapshot.features).map(([key, value]) => (
                  <View key={key} style={styles.featureItem}>
                    <Text style={styles.featureLabel}>{key.toUpperCase()}</Text>
                    <Text style={styles.featureValue}>
                      {value !== null && value !== undefined ? value.toFixed(2) : "--"}
                    </Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        </>
      ) : (
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateIcon}>📊</Text>
          <Text style={styles.emptyStateText}>No wellness data available</Text>
          <Text style={styles.emptyStateSubtext}>
            Pull down to refresh or send a chat message to generate wellness data.
          </Text>
        </View>
      )}

      {history.length > 0 && (
        <View style={styles.historyCard}>
          <Text style={styles.sectionTitle}>📜 Recent History</Text>
          <FlatList
            data={history.slice(0, 10)}
            keyExtractor={(item) => item.id}
            scrollEnabled={false}
            renderItem={({ item }) => (
              <View style={styles.listItem}>
                <View style={styles.listItemHeader}>
                  <Text style={styles.listValue}>PWI: {item.pwi ? item.pwi.toFixed(1) : "--"}</Text>
                  <StatusBadge status={item.status} />
                </View>
                <Text style={styles.listTimestamp}>
                  {item.timestamp || "Recent"}
                </Text>
              </View>
            )}
          />
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
  card: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 24,
    margin: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    alignItems: "center",
  },
  cardTitle: {
    fontSize: 16,
    color: "#6b7280",
    marginBottom: 8,
  },
  cardValue: {
    fontSize: 56,
    fontWeight: "700",
    marginBottom: 12,
  },
  cardTimestamp: {
    fontSize: 12,
    color: "#9ca3af",
    marginTop: 8,
  },
  statusBadge: {
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 2,
  },
  statusBadgeText: {
    fontSize: 14,
    fontWeight: "600",
  },
  chartCard: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 16,
    margin: 16,
    marginTop: 0,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  chartContainer: {
    marginTop: 16,
  },
  chart: {
    height: 150,
    position: "relative",
  },
  chartAxis: {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    width: 30,
    justifyContent: "space-between",
    paddingVertical: 4,
  },
  chartAxisLabel: {
    fontSize: 10,
    color: "#6b7280",
  },
  chartLineContainer: {
    position: "absolute",
    left: 40,
    right: 0,
    top: 0,
    bottom: 0,
  },
  chartLine: {
    position: "absolute",
    height: 2,
    backgroundColor: "#4f46e5",
    transformOrigin: "left center",
  },
  chartPoint: {
    position: "absolute",
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#4f46e5",
  },
  chartPlaceholder: {
    height: 150,
    justifyContent: "center",
    alignItems: "center",
  },
  chartPlaceholderText: {
    color: "#9ca3af",
    fontSize: 14,
  },
  featuresCard: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 16,
    margin: 16,
    marginTop: 0,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  featuresGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginTop: 12,
  },
  featureItem: {
    width: "50%",
    padding: 12,
    borderWidth: 1,
    borderColor: "#e5e7eb",
    borderRadius: 8,
    marginBottom: 8,
    marginRight: 8,
  },
  featureLabel: {
    fontSize: 12,
    color: "#6b7280",
    marginBottom: 4,
  },
  featureValue: {
    fontSize: 18,
    fontWeight: "600",
    color: "#1f2937",
  },
  historyCard: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 16,
    margin: 16,
    marginTop: 0,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 12,
    color: "#1f2937",
  },
  listItem: {
    padding: 12,
    marginBottom: 8,
    borderRadius: 8,
    backgroundColor: "#f9fafb",
    borderWidth: 1,
    borderColor: "#e5e7eb",
  },
  listItemHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  listValue: {
    fontSize: 16,
    fontWeight: "600",
    color: "#1f2937",
  },
  listTimestamp: {
    fontSize: 12,
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
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: "#6b7280",
    textAlign: "center",
  },
});
