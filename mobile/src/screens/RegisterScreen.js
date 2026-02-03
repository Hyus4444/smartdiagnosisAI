import { View, Text, TextInput, Button, StyleSheet } from "react-native";
import { useContext, useState } from "react";
import { AuthContext } from "../context/AuthContext";

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
    <View style={styles.container}>
      <Text style={styles.label}>Nombre completo</Text>
      <TextInput
        style={styles.input}
        value={fullName}
        onChangeText={setFullName}
        autoCapitalize="words"
      />

      <Text style={styles.label}>Email</Text>
      <TextInput
        style={styles.input}
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />

      <Text style={styles.label}>Contraseña</Text>
      <TextInput
        style={styles.input}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Text style={{ fontSize: 12, color: "#666", textAlign: "center" }}>
        La contraseña debe tener al menos 7 caracteres y contener un número o un
        símbolo especial
      </Text>

      <Button title="Crear cuenta" onPress={handleRegister} />

      <View style={{ height: 10 }} />
      <Button
        title="Volver a Login"
        onPress={() => navigation.navigate("Login")}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, gap: 10 },
  title: { fontSize: 22, fontWeight: "600", marginBottom: 10 },
  label: { fontSize: 12, color: "#666" },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: "#fff",
  },
});
