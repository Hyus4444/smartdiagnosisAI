/*Pantalla para crear un nuevo paciente, con campos para el nombre completo, tipo y número de documento, fecha de nacimiento y género. Incluye validación de campos 
y manejo de errores al enviar la información al backend. Al guardar, redirige a la pantalla de inicio para que se actualice la lista de pacientes.*/
import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import api from "../config/api";

export default function CreatePatientScreen() {
  const navigation = useNavigation();

  const [fullName, setFullName] = useState("");
  const [documentType, setDocumentType] = useState("CC");
  const [documentNumber, setDocumentNumber] = useState("");
  const [birthDate, setBirthDate] = useState(""); // YYYY-MM-DD
  const [gender, setGender] = useState("M");

  const [loading, setLoading] = useState(false);

  const validate = () => {
    if (!fullName.trim()) return "Full name is required.";
    if (!documentType.trim()) return "Document type is required.";
    if (!documentNumber.trim()) return "Document number is required.";
    if (!birthDate.trim()) return "Birth date is required (YYYY-MM-DD).";
    // validación simple YYYY-MM-DD
    if (!/^\d{4}-\d{2}-\d{2}$/.test(birthDate.trim())) {
      return "Birth date format must be YYYY-MM-DD.";
    }
    if (!gender.trim()) return "Gender is required.";
    return null;
  };

  const handleCreate = async () => {
    const errMsg = validate();
    if (errMsg) {
      Alert.alert("Validation", errMsg);
      return;
    }

    setLoading(true);
    try {
      const payload = {
        full_name: fullName.trim(),
        document_type: documentType.trim().toUpperCase(),
        document_number: documentNumber.trim(),
        birth_date: birthDate.trim(),
        gender: gender.trim().toUpperCase(),
      };

      await api.post("/patients", payload);

      // Señal para que Home refresque
      navigation.navigate("Home", { refresh: Date.now() });
    } catch (err) {
      const status = err?.response?.status;
      const data = err?.response?.data;

      if (status === 409) {
        Alert.alert("Duplicate", data?.detail || "Patient already exists.");
        return;
      }

      if (status === 422) {
        Alert.alert("Validation", "Invalid fields. Check values and try again.");
        return;
      }

      if (status === 401) {
        Alert.alert("Session", "Unauthorized. Please login again.");
        return;
      }

      Alert.alert("Error", data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create patient</Text>

      <View style={styles.field}>
        <Text style={styles.label}>Full name</Text>
        <TextInput
          style={styles.input}
          value={fullName}
          onChangeText={setFullName}
          placeholder="e.g. Maria Lopez"
          autoCapitalize="words"
        />
      </View>

      <View style={styles.row}>
        <View style={[styles.field, { flex: 1 }]}>
          <Text style={styles.label}>Document type</Text>
          <TextInput
            style={styles.input}
            value={documentType}
            onChangeText={setDocumentType}
            placeholder="CC"
            autoCapitalize="characters"
          />
        </View>

        <View style={[styles.field, { flex: 2 }]}>
          <Text style={styles.label}>Document number</Text>
          <TextInput
            style={styles.input}
            value={documentNumber}
            onChangeText={setDocumentNumber}
            placeholder="e.g. 987654321"
            keyboardType="default"
          />
        </View>
      </View>

      <View style={styles.row}>
        <View style={[styles.field, { flex: 1 }]}>
          <Text style={styles.label}>Birth date</Text>
          <TextInput
            style={styles.input}
            value={birthDate}
            onChangeText={setBirthDate}
            placeholder="YYYY-MM-DD"
          />
        </View>

        <View style={[styles.field, { flex: 1 }]}>
          <Text style={styles.label}>Gender</Text>
          <TextInput
            style={styles.input}
            value={gender}
            onChangeText={setGender}
            placeholder="M / F"
            autoCapitalize="characters"
          />
        </View>
      </View>

      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleCreate}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator />
        ) : (
          <Text style={styles.buttonText}>Save</Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.link}
        onPress={() => navigation.goBack()}
        disabled={loading}
      >
        <Text style={styles.linkText}>Cancel</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fff" },
  title: { fontSize: 18, fontWeight: "600", marginBottom: 16 },
  field: { marginBottom: 12 },
  label: { fontSize: 12, color: "#666", marginBottom: 6 },
  input: {
    borderWidth: 1,
    borderColor: "#e0e0e0",
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
  },
  row: { flexDirection: "row", gap: 12 },
  button: {
    marginTop: 10,
    backgroundColor: "#000",
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
  },
  buttonDisabled: { opacity: 0.7 },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  link: { marginTop: 12, alignItems: "center" },
  linkText: { color: "#444" },
});
