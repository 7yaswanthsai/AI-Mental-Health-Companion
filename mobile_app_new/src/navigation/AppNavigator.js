import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import LoginScreen from "../screens/LoginScreen";
import ChatScreen from "../screens/ChatScreen";
import WellnessScreen from "../screens/WellnessScreen";
import RecommendationsScreen from "../screens/RecommendationsScreen";
import { useAuth } from "../context/AuthContext";

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
  const { token } = useAuth();

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: "#ffffff",
          },
          headerTintColor: "#1f2937",
          headerTitleStyle: {
            fontWeight: "600",
          },
          headerShadowVisible: true,
        }}
      >
        {token ? (
          <>
            <Stack.Screen
              name="Chat"
              component={ChatScreen}
              options={{
                title: "💬 Chat",
                headerBackVisible: false,
              }}
            />
            <Stack.Screen
              name="Wellness"
              component={WellnessScreen}
              options={{
                title: "🩺 Wellness Dashboard",
              }}
            />
            <Stack.Screen
              name="Recommendations"
              component={RecommendationsScreen}
              options={{
                title: "💡 Recommendations",
              }}
            />
          </>
        ) : (
          <Stack.Screen
            name="Login"
            component={LoginScreen}
            options={{
              headerShown: false,
            }}
          />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
