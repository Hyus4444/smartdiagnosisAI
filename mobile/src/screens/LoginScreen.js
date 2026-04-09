/*LoginScreen permite a los usuarios ingresar su email y contraseña para acceder a la aplicación. Incluye validación de campos y manejo de errores al intentar iniciar sesión.*/
import { View, Text, TextInput, TouchableOpacity, Animated } from "react-native";
import { useState, useContext, useRef, useEffect } from "react";
import { AuthContext } from "../context/AuthContext";
import { globalStyles } from "../styles/globalStyles";
import AppModal from "../components/AppModal";

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [modalData, setModalData] = useState({ visible: false, title: "", message: "", tone: "info" });
  const { login } = useContext(AuthContext);

  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 260,
      useNativeDriver: true,
    }).start();
  }, [fadeAnim]);

  const openModal = (title, message, tone = "info") => {
    setModalData({ visible: true, title, message, tone });
  };

  const handleLogin = async () => {
    if (!email || !password) {
      openModal("Campos incompletos", "Por favor completa todos los campos.", "error");
      return;
    }
    try {
      await login(email, password);
    } catch (error) {
      if (error.response?.data?.detail === "Invalid credentials") {
        openModal("Credenciales inválidas", "Email o contraseña incorrectos.", "error");
      } else {
        console.log("Login error:", error);
        openModal("Error", "Error de conexión.", "error");
      }
    }
  };

  return (
    <Animated.View style={[globalStyles.paddedContainer, { justifyContent: "center", opacity: fadeAnim }]}>
      <View style={globalStyles.card}>
        <Text style={[globalStyles.title, { marginBottom: 16 }]}>Bienvenido</Text>

        <Text style={globalStyles.label}>Email</Text>
        <TextInput
          style={globalStyles.input}
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
        />

        <Text style={globalStyles.label}>Contraseña</Text>
        <TextInput
          style={globalStyles.input}
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

        <TouchableOpacity style={globalStyles.buttonPrimary} onPress={() => handleLogin()}>
          <Text style={globalStyles.buttonTextPrimary}>Iniciar sesión</Text>
        </TouchableOpacity>

        <Text style={[globalStyles.mutedText, { marginTop: 14, textAlign: "center" }]}>¿No tienes una cuenta?</Text>
        <TouchableOpacity style={[globalStyles.buttonOutline, { marginTop: 8 }]} onPress={() => navigation.navigate("Register")}>
          <Text style={globalStyles.buttonTextOutline}>Registrarse</Text>
        </TouchableOpacity>
      </View>

      <AppModal
        visible={modalData.visible}
        title={modalData.title}
        message={modalData.message}
        tone={modalData.tone}
        onPrimary={() => setModalData({ visible: false, title: "", message: "", tone: "info" })}
      />
    </Animated.View>
  );
}
