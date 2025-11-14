import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, FlatList, RefreshControl, ActivityIndicator, Alert } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { createApiClient } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function WellnessScreen({ navigation }) {
  const { token, subjectId } = useAuth();
  const [currentSnapshot, setCurrentSnapshot] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchWellness = async () => {
    setLoading(true);
    try {
      const api = createApiClient(token);
      const response = await api.get(`/wellness/${subjectId}`);
      const snapshot = response.data;
      setCurrentSnapshot(snapshot);
      setHistory((prev) => [
        { id: Date.now().toString(), ...snapshot },
        ...prev.slice(0, 19),
      ]);
    } catch (error) {
      console.error("Wellness fetch failed", error);
      Alert.alert("Error", "Unable to fetch wellness data.");
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

  return (
    <View style={styles.container}>
      {currentSnapshot ? (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Current PWI</Text>
          <Text style={styles.cardValue}>{currentSnapshot.pwi ? currentSnapshot.pwi.toFixed(2) : "--"}</Text>
          <Text style={styles.cardStatus}>{currentSnapshot.status || "Unknown"}</Text>
        </View>
      ) : (
        <Text style={styles.placeholder}>No wellness data yet.</Text>
      )}

      <Text style={styles.sectionTitle}>Recent Snapshots</Text>
      <FlatList
        data={history}
        keyExtractor={(item) => item.id}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={fetchWellness} />}
        renderItem={({ item }) => (
          <View style={styles.listItem}>
            <Text style={styles.listTimestamp}>{item.timestamp || "recent"}</Text>
            <Text style={styles.listValue}>PWI: {item.pwi ? item.pwi.toFixed(2) : "--"}</Text>
            <Text style={styles.listStatus}>Status: {item.status || "Unknown"}</Text>
          </View>
        )}
        ListEmptyComponent={
          loading ? <ActivityIndicator /> : <Text style={styles.placeholder}>Pull to refresh for data.</Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: "#f9fafb",
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: 16,
    padding: 24,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 16,
    color: "#6b7280",
  },
  cardValue: {
    fontSize: 40,
    fontWeight: "700",
    marginTop: 8,
    color: "#111827",
  },
  cardStatus: {
    fontSize: 18,
    marginTop: 4,
    color: "#2563eb",
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 8,
    color: "#111827",
  },
  listItem: {
    backgroundColor: "#fff",
    padding: 16,
    marginBottom: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#e5e7eb",
  },
  listTimestamp: {
    fontSize: 12,
    color: "#9ca3af",
    marginBottom: 4,
  },
  listValue: {
    fontSize: 16,
    fontWeight: "600",
    color: "#111827",
  },
  listStatus: {
    fontSize: 14,
    color: "#4b5563",
    marginTop: 2,
  },
  placeholder: {
    textAlign: "center",
    color: "#6b7280",
    marginVertical: 16,
  },
});


