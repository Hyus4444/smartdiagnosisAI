/*RegisterScreen permite a los usuarios crear una nueva cuenta ingresando su email y contraseña. Incluye validación de campos y manejo de errores al intentar registrarse.
Al registrarse exitosamente, redirige a la pantalla de login para que el usuario pueda iniciar sesión con su nueva cuenta.*/
import { View, Text, TextInput, TouchableOpacity } from "react-native";
import { useContext, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import { globalStyles } from "../styles/globalStyles";

export default function RegisterScreen({ navigation }) {
  const { register } = useContext(AuthContext);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = async () => {
    try {
      if (!fullName || !email || !password) {
        alert("Por favor completa todos los campos");
        return;
      }
      await register({
        full_name: fullName,
        email,
        password,
      });
      alert("Usuario registrado.");
      navigation.navigate("Login");
    } catch (error) {
      if (error.response?.data?.detail[0].msg.includes("email address")) {
        alert("Formato de email inválido");
        return;
      } else if (error.response?.data?.detail === "Email ya registrado") {
        alert("El email ya está en uso. Usa otro email.");
        return;
      } else if (error.response?.data?.detail === "Contraseña invalida") {
        alert(
          "La contraseña debe tener al menos 7 caracteres y contener un número o un símbolo especial",
        );
        return;
      } else {
        alert("Error de conexión");
        return;
      }
    }
  };

  return (
    <View style={[globalStyles.paddedContainer, { gap: 10 }]}>
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
      <Text style={[globalStyles.mutedText, { textAlign: "center" }]}>
        La contraseña debe tener al menos 7 caracteres y contener un número o un
        símbolo especial
      </Text>

      <TouchableOpacity
        style={globalStyles.buttonPrimary}
        onPress={() => handleRegister()}
      >
        <Text style={globalStyles.buttonTextPrimary}>Registrarse</Text>
      </TouchableOpacity>

      <View/>
      <TouchableOpacity
        style={globalStyles.buttonSecondary}
        onPress={() => navigation.navigate("Login")}
      >
        <Text style={globalStyles.buttonTextPrimary}>Volver a Login</Text>
      </TouchableOpacity>
    </View>
  );
}