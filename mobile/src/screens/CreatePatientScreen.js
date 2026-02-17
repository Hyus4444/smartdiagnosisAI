/*Pantalla para crear un nuevo paciente, con campos para el nombre completo, tipo y número de documento, fecha de nacimiento y género. Incluye validación de campos 
y manejo de errores al enviar la información al backend. Al guardar, redirige a la pantalla de inicio para que se actualice la lista de pacientes.*/
import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";

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
        Alert.alert(
          "Validation",
          "Invalid fields. Check values and try again.",
        );
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
    <View style={globalStyles.container}>
      <View style={globalStyles.paddedContainer}>
        <View style={{ marginBottom: 12 }}>
          <Text style={globalStyles.label}>Nombre completo</Text>
          <TextInput
            style={globalStyles.input}
            value={fullName}
            onChangeText={setFullName}
            placeholder="e.g. Maria Lopez"
            autoCapitalize="words"
          />
        </View>
        <View style={globalStyles.row}>
          <View style={{ flex: 1, marginBottom: 12 }}>
            <Text style={globalStyles.label}>Tipo de documento</Text>
            <TextInput
              style={globalStyles.input}
              value={documentType}
              onChangeText={setDocumentType}
              placeholder="CC"
              autoCapitalize="characters"
            />
          </View>

          <View style={{ flex: 2, marginBottom: 12 }}>
            <Text style={globalStyles.label}>Número de documento</Text>
            <TextInput
              style={globalStyles.input}
              value={documentNumber}
              onChangeText={setDocumentNumber}
              placeholder="e.g. 987654321"
              keyboardType="default"
            />
          </View>
        </View>

        <View style={globalStyles.row}>
          <View style={{ flex: 1, marginBottom: 12 }}>
            <Text style={globalStyles.label}>Fecha de nacimiento</Text>
            <TextInput
              style={globalStyles.input}
              value={birthDate}
              onChangeText={setBirthDate}
              placeholder="YYYY-MM-DD"
            />
          </View>

          <View style={{ flex: 1, marginBottom: 12 }}>
            <Text style={globalStyles.label}>Género</Text>
            <TextInput
              style={globalStyles.input}
              value={gender}
              onChangeText={setGender}
              placeholder="M / F"
              autoCapitalize="characters"
            />
          </View>
        </View>
      </View>
      <View style={globalStyles.footer}>
        {/* Acciones inferiores */}
        <TouchableOpacity
          style={[globalStyles.buttonSecondary, { marginTop: 8, flex: 1 }]}
          onPress={() => navigation.goBack()}
        >
          <Text style={globalStyles.buttonTextPrimary}>Cancelar</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[globalStyles.buttonPrimary, { marginTop: 8, flex: 1 }]}
          onPress={handleCreate}
        >
          <Text style={globalStyles.buttonTextPrimary}>Guardar</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
