import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { useContext, useLayoutEffect } from "react";
import { useNavigation } from "@react-navigation/native";
import { AuthContext } from "../context/AuthContext";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";

export default function AccountScreen() {
  const navigation = useNavigation();
  const { logout } = useContext(AuthContext);

  useLayoutEffect(() => {
    navigation.setOptions({ title: "Configuración" });
  }, [navigation]);

  const handleLogout = () => {
    Alert.alert(
      "Cerrar sesión",
      "¿Seguro que deseas cerrar sesión?",
      [
        { text: "Cancelar", style: "cancel" },
        {
          text: "Cerrar sesión",
          style: "destructive",
          onPress: () => {
            // opcional: limpiar header por si tu api.js cachea el Authorization
            try {
              delete api.defaults.headers.common.Authorization;
            } catch (_) {}
            logout();
          },
        },
      ],
      { cancelable: true }
    );
  };

  return (
    <View style={globalStyles.paddedContainer}>

      <View style={globalStyles.card}>
        <Text style={globalStyles.title}>Opciones</Text>

        <TouchableOpacity
          style={globalStyles.rowButton}
          onPress={() => Alert.alert("Próximamente", "Pantalla en desarrollo.")}
        >
          <Text style={globalStyles.text}>Perfil</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={globalStyles.rowButton}
          onPress={() => Alert.alert("Próximamente", "Pantalla en desarrollo.")}
        >
          <Text style={globalStyles.text}>Preferencias</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={globalStyles.rowButton}
          onPress={() => Alert.alert("Próximamente", "Pantalla en desarrollo.")}
        >
          <Text style={globalStyles.text}>Soporte</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={globalStyles.buttonSecondary} onPress={handleLogout}>
        <Text style={globalStyles.buttonTextPrimary}>Cerrar sesión</Text>
      </TouchableOpacity>
    </View>
  );
}