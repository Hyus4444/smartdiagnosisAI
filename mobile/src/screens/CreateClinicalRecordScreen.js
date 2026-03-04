import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, Alert, Switch } from "react-native";
import { useNavigation, useRoute } from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";

export default function CreateClinicalRecordScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { patientId } = route.params;

  const [loading, setLoading] = useState(false);

  // Campos V1 (inputs)
  const [bloodGlucose, setBloodGlucose] = useState("");
  const [hba1c, setHba1c] = useState("");
  const [weightKg, setWeightKg] = useState("");
  const [heightCm, setHeightCm] = useState("");
  const [systolic, setSystolic] = useState("");
  const [diastolic, setDiastolic] = useState("");
  const [heartDisease, setHeartDisease] = useState(false);
  const [notes, setNotes] = useState("");

  const handleSave = async () => {
    setLoading(true);
    try {
      const payload = {
        blood_glucose_level: Number(bloodGlucose),
        hba1c_level: Number(hba1c),
        weight_kg: Number(weightKg),
        height_cm: Number(heightCm),
        systolic_bp: Number(systolic),
        diastolic_bp: Number(diastolic),
        heart_disease: Boolean(heartDisease),
        notes: notes?.trim() ? notes.trim() : null,
      };

      // IMPORTANTE: el endpoint debe retornar el record creado (con id)
      const res = await api.post(`/patients/${patientId}/clinical-records`, payload);
      const created = res.data;

      // Ir directo al detalle del registro (y allí ver predicción)
      navigation.replace("ClinicalRecordDetail", {
        patientId,
        recordId: created.id,
      });
    } catch (err) {
      const status = err?.response?.status;
      const data = err?.response?.data;

      if (status === 404) {
        Alert.alert("No encontrado", data?.detail || "Paciente no encontrado.");
      } else if (status === 401) {
        Alert.alert("No autorizado", "Inicia sesión de nuevo.");
      } else if (status === 409) {
        Alert.alert("Conflicto", data?.detail || "Conflicto al crear registro.");
      } else if (status === 422) {
        Alert.alert("Validación", "Revisa los campos requeridos y formatos numéricos.");
      } else {
        Alert.alert("Error", data?.detail || err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={globalStyles.paddedContainer}>
      <Text style={globalStyles.title}>Nuevo registro clínico</Text>

      <Text style={globalStyles.label}>Glucosa (mg/dL)</Text>
      <TextInput
        style={globalStyles.input}
        value={bloodGlucose}
        onChangeText={setBloodGlucose}
        placeholder="Ej: 140"
        keyboardType="numeric"
      />

      <Text style={globalStyles.label}>HbA1c (%)</Text>
      <TextInput
        style={globalStyles.input}
        value={hba1c}
        onChangeText={setHba1c}
        placeholder="Ej: 6.8"
        keyboardType="numeric"
      />

      <Text style={globalStyles.label}>Peso (kg)</Text>
      <TextInput
        style={globalStyles.input}
        value={weightKg}
        onChangeText={setWeightKg}
        placeholder="Ej: 80"
        keyboardType="numeric"
      />

      <Text style={globalStyles.label}>Estatura (cm)</Text>
      <TextInput
        style={globalStyles.input}
        value={heightCm}
        onChangeText={setHeightCm}
        placeholder="Ej: 175"
        keyboardType="numeric"
      />

      <Text style={globalStyles.label}>Presión sistólica (mmHg)</Text>
      <TextInput
        style={globalStyles.input}
        value={systolic}
        onChangeText={setSystolic}
        placeholder="Ej: 130"
        keyboardType="numeric"
      />

      <Text style={globalStyles.label}>Presión diastólica (mmHg)</Text>
      <TextInput
        style={globalStyles.input}
        value={diastolic}
        onChangeText={setDiastolic}
        placeholder="Ej: 85"
        keyboardType="numeric"
      />

      <View style={globalStyles.row}>
        <Text style={globalStyles.label}>Enfermedad cardíaca</Text>
        <Switch value={heartDisease} onValueChange={setHeartDisease} />
      </View>

      <Text style={globalStyles.label}>Notas (opcional)</Text>
      <TextInput
        style={globalStyles.textarea}
        value={notes}
        onChangeText={setNotes}
        placeholder="Observaciones…"
        multiline
        textAlignVertical="top"
      />

      <View style={globalStyles.footer}>
        <TouchableOpacity
          style={[globalStyles.buttonSecondary, { marginTop: 8, flex: 1 }]}
          onPress={() => navigation.goBack()}
          disabled={loading}
        >
          <Text style={globalStyles.buttonTextPrimary}>Cancelar</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[globalStyles.buttonPrimary, { marginTop: 8, flex: 1 }]}
          onPress={handleSave}
          disabled={loading}
        >
          <Text style={globalStyles.buttonTextPrimary}>
            {loading ? "Guardando…" : "Guardar"}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}