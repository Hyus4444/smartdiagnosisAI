import { View, Text, TouchableOpacity, Alert, Animated } from "react-native";
import { useLayoutEffect, useRef, useEffect } from "react";
import { useNavigation } from "@react-navigation/native";
import { globalStyles } from "../styles/globalStyles";

export default function AccountScreen() {
  const navigation = useNavigation();
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(12)).current;

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

        <TouchableOpacity
          style={globalStyles.rowButton}
          onPress={() => Alert.alert("Próximamente", "Preferencias en desarrollo.")}
        >
          <Text style={globalStyles.rowButtonText}>Preferencias</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={globalStyles.rowButton}
          onPress={() => Alert.alert("Próximamente", "Centro de soporte en desarrollo.")}
        >
          <Text style={globalStyles.rowButtonText}>Soporte</Text>
        </TouchableOpacity>
      </Animated.View>
    </View>
  );
}
