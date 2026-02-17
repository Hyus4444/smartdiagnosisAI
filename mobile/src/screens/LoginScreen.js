/*LoginScreen permite a los usuarios ingresar su email y contraseña para acceder a la aplicación. Incluye validación de campos y manejo de errores al intentar iniciar sesión.*/
import { View, Text, TextInput, TouchableOpacity} from "react-native";
import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { globalStyles } from "../styles/globalStyles";

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useContext(AuthContext);

  const handleLogin = async () => {
    if (!email || !password) {
      alert("Por favor completa todos los campos");
      return;
    }
    try {
      await login(email, password);
    } catch (error) {
      if (error.response?.data?.detail === "Invalid credentials") {
        alert("Email o contraseña incorrectos");
      } else {
        console.log("Login error:", error);
        alert("Error de conexión");
      }
    }
  };

  return (
    <View style={[globalStyles.paddedContainer, { justifyContent: "center" }]}>
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

      <TouchableOpacity
        style={globalStyles.buttonPrimary}
        onPress={() => handleLogin()}
      >
        <Text style={globalStyles.buttonTextPrimary}>Iniciar sesión</Text>
      </TouchableOpacity>

      <Text
        style={[globalStyles.mutedText, { marginTop: 10, textAlign: "center" }]}
      >
        ¿No tienes una cuenta?
      </Text>
      <TouchableOpacity
        style={globalStyles.buttonSecondary} 
        onPress={() => navigation.navigate("Register")}
      >
        <Text style={globalStyles.buttonTextPrimary}>Registrarse</Text>
      </TouchableOpacity>
    </View>
  );
}
