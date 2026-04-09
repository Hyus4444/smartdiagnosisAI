import { View, Text, TouchableOpacity, Alert, Animated } from "react-native";
import { useContext, useLayoutEffect, useRef, useEffect } from "react";
import { useNavigation } from "@react-navigation/native";
import { globalStyles } from "../styles/globalStyles";
import { AuthContext } from "../context/AuthContext";

export default function AccountScreen() {
  const navigation = useNavigation();
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(12)).current;
  const { token, logout } = useContext(AuthContext);

  useLayoutEffect(() => {
    navigation.setOptions({ title: "Configuración" });
  }, [navigation]);

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 350,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 350,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, slideAnim]);


  const handleLogout = () => {
    Alert.alert("Cerrar sesión", "¿Deseas cerrar sesión ahora?", [
      { text: "Cancelar", style: "cancel" },
      {
        text: "Cerrar sesión",
        style: "destructive",
        onPress: () => {
          try {
            delete api.defaults.headers.common.Authorization;
          } catch (_) {}
          logout();
        },
      },
    ]);
  };
  return (
    <View style={globalStyles.paddedContainer}>
      <View style={globalStyles.heroCard}>
        <Text style={globalStyles.heroTitle}>Centro de configuración</Text>
        <Text style={globalStyles.heroText}>
          Ajustes iniciales para una experiencia clínica profesional y ordenada.
        </Text>
      </View>

      <Animated.View
        style={[
          globalStyles.card,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }],
          },
        ]}
      >
        <Text style={globalStyles.subtitle}>Opciones de cuenta</Text>

        <TouchableOpacity
          style={globalStyles.rowButton}
          onPress={() => navigation.navigate("Profile")}
        >
          <Text style={globalStyles.rowButtonText}>Perfil</Text>
        </TouchableOpacity>
      </Animated.View>
      <TouchableOpacity style={globalStyles.buttonSecondary} onPress={handleLogout}>
        <Text style={globalStyles.buttonTextPrimary}>Cerrar sesión</Text>
      </TouchableOpacity>
    </View>
  );
}
