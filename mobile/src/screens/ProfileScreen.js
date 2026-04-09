import { useEffect, useMemo, useRef } from "react";
import { View, Text, Animated } from "react-native";
import { globalStyles } from "../styles/globalStyles";

export default function ProfileScreen() {

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(10)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 420,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 420,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, slideAnim]);

  const profileData = useMemo(() => {
    return {
      nombre: currentUser?.name || "Usuario desconocido",
      rol: "Cuenta clínica",
      estado: "Sesión activa",
    };
  }, []);

  const initials = "PS";

  return (
    <View style={globalStyles.paddedContainer}>
      <Animated.View
        style={[
          globalStyles.card,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }],
          },
        ]}
      >
        <View style={globalStyles.profileAvatar}>
          <Text style={globalStyles.profileAvatarText}>{initials}</Text>
        </View>

        <Text style={globalStyles.title}>Perfil</Text>
        <Text style={globalStyles.heroText}>Información personal de la cuenta activa.</Text>

        <View style={globalStyles.sectionSpacing}>
          <Text style={globalStyles.label}>Nombre</Text>
          <Text style={globalStyles.profileValue}>{profileData.nombre}</Text>

          <Text style={globalStyles.label}>Tipo de cuenta</Text>
          <Text style={globalStyles.profileValue}>{profileData.rol}</Text>

          <Text style={globalStyles.label}>Estado</Text>
          <Text style={globalStyles.profileValue}>{profileData.estado}</Text>

          <Text style={globalStyles.label}>Credencial de sesión</Text>
          <Text style={globalStyles.profileValue}>{profileData.credencial}</Text>
        </View>
      </Animated.View>

      
    </View>
  );
}
