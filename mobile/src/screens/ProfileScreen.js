import { useContext, useEffect, useMemo, useRef, useState, useCallback } from "react";
import { View, Text, Animated, TouchableOpacity, ActivityIndicator } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { AuthContext } from "../context/AuthContext";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";
import AppModal from "../components/AppModal";

export default function ProfileScreen() {
  const { token, user, logout, refreshUser } = useContext(AuthContext);

  const [loadingProfile, setLoadingProfile] = useState(false);
  const [logoutModalVisible, setLogoutModalVisible] = useState(false);
  const [errorModalVisible, setErrorModalVisible] = useState(false);

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(10)).current;

  const fetchProfile = useCallback(async () => {
    setLoadingProfile(true);
    const data = await refreshUser();
    if (!data) {
      setErrorModalVisible(true);
    }
    setLoadingProfile(false);
  }, [refreshUser]);

  useFocusEffect(
    useCallback(() => {
      fetchProfile();
    }, [fetchProfile])
  );

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
    const tokenShort = token ? `${token.slice(0, 12)}...` : "No disponible";
    return {
      nombre: user?.full_name || "No disponible",
      correo: user?.email || "No disponible",
      estado: "Sesión activa",
      credencial: tokenShort,
      id: user?.id || "No disponible",
    };
  }, [token, user]);

  const initials = useMemo(() => {
    if (!user?.full_name) return "PS";
    return user.full_name
      .split(" ")
      .slice(0, 2)
      .map((word) => word[0]?.toUpperCase())
      .join("");
  }, [user?.full_name]);

  const handleLogout = () => {
    try {
      delete api.defaults.headers.common.Authorization;
    } catch (_) {}
    setLogoutModalVisible(false);
    logout();
  };

  return (
    <View style={globalStyles.paddedContainer}>
      {loadingProfile ? (
        <View style={globalStyles.cardCenter}>
          <ActivityIndicator size="small" color="#0A6FAE" />
          <Text style={globalStyles.smallText}>Cargando información del perfil...</Text>
        </View>
      ) : null}

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

          <Text style={globalStyles.label}>Correo</Text>
          <Text style={globalStyles.profileValue}>{profileData.correo}</Text>

          <Text style={globalStyles.label}>Estado</Text>
          <Text style={globalStyles.profileValue}>{profileData.estado}</Text>

          <Text style={globalStyles.label}>ID de usuario</Text>
          <Text style={globalStyles.profileValue}>{profileData.id}</Text>

          <Text style={globalStyles.label}>Credencial de sesión</Text>
          <Text style={globalStyles.profileValue}>{profileData.credencial}</Text>
        </View>
      </Animated.View>

      <TouchableOpacity
        style={globalStyles.buttonSecondary}
        onPress={() => setLogoutModalVisible(true)}
      >
        <Text style={globalStyles.buttonTextPrimary}>Cerrar sesión</Text>
      </TouchableOpacity>

      <AppModal
        visible={logoutModalVisible}
        title="Cerrar sesión"
        message="¿Deseas cerrar sesión ahora?"
        tone="info"
        secondaryLabel="Cancelar"
        onSecondary={() => setLogoutModalVisible(false)}
        primaryLabel="Cerrar sesión"
        onPrimary={handleLogout}
      />

      <AppModal
        visible={errorModalVisible}
        title="Perfil no disponible"
        message="No se pudo cargar tu información personal. Puedes reintentar entrando nuevamente a esta pantalla."
        tone="error"
        onPrimary={() => setErrorModalVisible(false)}
      />
    </View>
  );
}
