import { View, Text, TextInput, Button, StyleSheet } from "react-native";
import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";

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
    <View style={styles.container}>
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

      <View style={styles.button}>
        <Button title="Login" onPress={handleLogin} />
      </View>

      <Text style={styles.footerText}>¿No tienes una cuenta?</Text>
      <Button
        title="Registrarse"
        onPress={() => navigation.navigate("Register")}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    justifyContent: "center",
  },
  title: {
    fontSize: 22,
    fontWeight: "600",
    marginBottom: 24,
    textAlign: "center",
  },
  label: {
    fontSize: 12,
    color: "#666",
    marginBottom: 4,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    marginBottom: 12,
    backgroundColor: "#fff",
  },
  button: {
    marginTop: 8,
    marginBottom: 16,
  },
  footerText: {
    textAlign: "center",
    marginBottom: 6,
  },
});
