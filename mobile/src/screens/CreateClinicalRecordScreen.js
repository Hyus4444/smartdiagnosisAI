import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
} from "react-native";
import { useNavigation, useRoute } from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";

export default function CreateClinicalRecordScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { patientId } = route.params;

  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    const value = content.trim();
    setLoading(true);
    try {
      // Ajusta la clave si tu schema no se llama "content"
      const payload = { content: value };
      await api.post(`/patients/${patientId}/clinical-records`, payload);

      // Volver al detalle: ahí se refresca la lista con useFocusEffect
      navigation.goBack();
    } catch (err) {
      const status = err?.response?.status;
      const data = err?.response?.data;

      if (status === 404) {
        Alert.alert("Not found", data?.detail || "Patient not found.");
        return;
      }
      if (status === 401) {
        Alert.alert("Unauthorized", "Please login again.");
        return;
      }
      if (status === 422) {
        Alert.alert(
          "Validation",
          "Invalid payload. Check required fields in the schema.",
        );
        return;
      }

      Alert.alert("Error", data?.detail || err.message);
    } finally {
      Alert.alert("Nota clínica creada (placeholder)");
      setLoading(false);
    }
  };

  return (
    <View style={globalStyles.paddedContainer}>
      <Text style={globalStyles.label}>Contenido (placeholder)</Text>
      <TextInput
        style={globalStyles.textarea}
        value={content}
        onChangeText={setContent}
        placeholder="Escribe una nota clínica (placeholder)…"
        multiline
        textAlignVertical="top"
      />
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
          onPress={handleSave}
        >
          <Text style={globalStyles.buttonTextPrimary}>Guardar</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}