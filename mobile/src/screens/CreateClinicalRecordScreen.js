import { useState, useRef, useEffect } from "react";
import { View, Text, TextInput, TouchableOpacity, Switch, Animated, ScrollView } from "react-native";
import { useNavigation, useRoute } from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";
import AppModal from "../components/AppModal";

export default function CreateClinicalRecordScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { patientId } = route.params;

  const [loading, setLoading] = useState(false);
  const [modalData, setModalData] = useState({ visible: false, title: "", message: "", tone: "info" });

  const [bloodGlucose, setBloodGlucose] = useState("");
  const [hba1c, setHba1c] = useState("");
  const [weightKg, setWeightKg] = useState("");
  const [heightCm, setHeightCm] = useState("");
  const [systolic, setSystolic] = useState("");
  const [diastolic, setDiastolic] = useState("");
  const [heartDisease, setHeartDisease] = useState(false);
  const [notes, setNotes] = useState("");

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

      const res = await api.post(`/patients/${patientId}/clinical-records`, payload);
      const created = res.data;

      navigation.replace("ClinicalRecordDetail", {
        patientId,
        recordId: created.id,
      });
    } catch (err) {
      const status = err?.response?.status;
      const data = err?.response?.data;

      if (status === 404) {
        openModal("No encontrado", data?.detail || "Paciente no encontrado.", "error");
      } else if (status === 401) {
        openModal("No autorizado", "Inicia sesión de nuevo.", "error");
      } else if (status === 409) {
        openModal("Conflicto", data?.detail || "Conflicto al crear registro.", "error");
      } else if (status === 422) {
        openModal("Validación", "Revisa los campos requeridos y formatos numéricos.", "error");
      } else {
        openModal("Error", data?.detail || err.message, "error");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={globalStyles.container}>
      <Animated.View style={{ flex: 1, opacity: fadeAnim }}>
        <ScrollView contentContainerStyle={[globalStyles.paddedContainer, { paddingBottom: 120 }]}>
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

          <View style={globalStyles.rowBetween}>
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
        </ScrollView>
      </Animated.View>

      <View style={globalStyles.footer}>
        <TouchableOpacity
          style={[globalStyles.buttonOutline, { marginTop: 8, flex: 1 }]}
          onPress={() => navigation.goBack()}
          disabled={loading}
        >
          <Text style={globalStyles.buttonTextOutline}>Cancelar</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[globalStyles.buttonPrimary, { marginTop: 8, flex: 1 }]}
          onPress={handleSave}
          disabled={loading}
        >
          <Text style={globalStyles.buttonTextPrimary}>{loading ? "Guardando…" : "Guardar"}</Text>
        </TouchableOpacity>
      </View>

      <AppModal
        visible={modalData.visible}
        title={modalData.title}
        message={modalData.message}
        tone={modalData.tone}
        onPrimary={() => setModalData({ visible: false, title: "", message: "", tone: "info" })}
      />
    </View>
  );
}
