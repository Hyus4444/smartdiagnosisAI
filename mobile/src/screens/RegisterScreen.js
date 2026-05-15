/*RegisterScreen permite a los usuarios crear una nueva cuenta ingresando su email y contraseña. Incluye validación de campos y manejo de errores al intentar registrarse.
Al registrarse exitosamente, redirige a la pantalla de login para que el usuario pueda iniciar sesión con su nueva cuenta.*/
import { View, Text, TextInput, TouchableOpacity, Animated } from "react-native";
import { useContext, useState, useRef, useEffect } from "react";
import { AuthContext } from "../context/AuthContext";
import { globalStyles } from "../styles/globalStyles";
import AppModal from "../components/AppModal";

export default function RegisterScreen({ navigation }) {
  const { register } = useContext(AuthContext);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [modalData, setModalData] = useState({ visible: false, title: "", message: "", tone: "info" });

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

  const handleRegister = async () => {
    try {
      if (!fullName || !email || !password) {
        openModal("Campos incompletos", "Por favor completa todos los campos.", "error");
        return;
      }
      await register({
        full_name: fullName,
        email,
        password,
      });
      openModal("Registro exitoso", "Usuario registrado correctamente.", "success");
      navigation.navigate("Login");
    } catch (error) {
      if (error.response?.data?.detail?.[0]?.msg?.includes("email address")) {
        openModal("Formato inválido", "Formato de email inválido.", "error");
      } else if (error.response?.data?.detail === "Email ya registrado") {
        openModal("Email en uso", "El email ya está en uso. Usa otro email.", "error");
      } else if (error.response?.data?.detail === "Contraseña invalida") {
        openModal(
          "Contraseña inválida",
          "La contraseña debe tener al menos 7 caracteres y contener un número o símbolo.",
          "error"
        );
      } else {
        openModal("Error", "Error de conexión.", "error");
      }
    }
  };

  return (
    <Animated.View style={[globalStyles.paddedContainer, { opacity: fadeAnim }]}>
      <View style={[globalStyles.card, { gap: 8 }]}>
        <Text style={globalStyles.title}>Crear cuenta</Text>

        <Text style={globalStyles.label}>Nombre completo</Text>
        <TextInput
          style={globalStyles.input}
          value={fullName}
          onChangeText={setFullName}
          autoCapitalize="words"
        />

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
        <Text style={[globalStyles.mutedText, { textAlign: "center" }]}>La contraseña debe tener al menos 7 caracteres y contener un número o símbolo especial.</Text>
        <TouchableOpacity style={globalStyles.buttonPrimary} onPress={() => handleRegister()}>
          <Text style={globalStyles.buttonTextPrimary}>Registrarse</Text>
        </TouchableOpacity>

        <TouchableOpacity style={globalStyles.buttonOutline} onPress={() => navigation.navigate("Login")}>
          <Text style={globalStyles.buttonTextOutline}>Volver a Login</Text>
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