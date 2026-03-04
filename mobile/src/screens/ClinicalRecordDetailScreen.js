import { View, Text, ActivityIndicator, TouchableOpacity, Alert } from "react-native";
import { useCallback, useLayoutEffect, useState } from "react";
import { useNavigation, useRoute, useFocusEffect } from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";

export default function ClinicalRecordDetailScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { patientId, recordId } = route.params;

  const [loading, setLoading] = useState(true);
  const [record, setRecord] = useState(null);

  const [predLoading, setPredLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);

  const fetchRecord = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/patients/${patientId}/clinical-records/${recordId}`);
      setRecord(res.data);
    } catch (err) {
      console.log("Error record detail:", err?.response?.status, err?.response?.data || err.message);
      setRecord(null);
    } finally {
      setLoading(false);
    }
  };

  const runPrediction = async () => {
    setPredLoading(true);
    try {
      const res = await api.post(`/patients/${patientId}/clinical-records/${recordId}/predict`);
      setPrediction(res.data);
    } catch (err) {
      const payload = err?.response?.data || err.message;
      Alert.alert("Error", payload?.detail || "No se pudo ejecutar la predicción.");
    } finally {
      setPredLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchRecord().then(() => {
        // Auto-predict al entrar (opcional). Si no lo quieres, quita esto.
        runPrediction();
      });
    }, [patientId, recordId])
  );

  useLayoutEffect(() => {
    navigation.setOptions({ title: "Registro clínico" });
  }, [navigation]);

  if (loading) {
    return (
      <View style={globalStyles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (!record) {
    return (
      <View style={globalStyles.center}>
        <Text>Registro no encontrado</Text>
      </View>
    );
  }

  const proba =
    prediction?.predicted_proba !== undefined ? Number(prediction.predicted_proba) : null;
  const label =
    prediction?.predicted_label !== undefined ? Number(prediction.predicted_label) : null;

  return (
    <View style={globalStyles.container}>
      <View style={globalStyles.card}>
        <Text style={globalStyles.title}>Reporte</Text>

        <Text style={globalStyles.subtitle}>Glucosa: {record.blood_glucose_level}</Text>
        <Text style={globalStyles.subtitle}>HbA1c: {record.hba1c_level}</Text>
        <Text style={globalStyles.subtitle}>Peso (kg): {record.weight_kg}</Text>
        <Text style={globalStyles.subtitle}>Estatura (cm): {record.height_cm}</Text>
        <Text style={globalStyles.subtitle}>IMC: {record.bmi}</Text>
        <Text style={globalStyles.subtitle}>
          Presión: {record.systolic_bp}/{record.diastolic_bp}
        </Text>
        <Text style={globalStyles.subtitle}>
          Hipertensión: {record.hypertension ? "Sí" : "No"}
        </Text>
        <Text style={globalStyles.subtitle}>
          Enfermedad cardíaca: {record.heart_disease ? "Sí" : "No"}
        </Text>
        {record.notes ? <Text style={globalStyles.subtitle}>Notas: {record.notes}</Text> : null}
      </View>

      <View style={globalStyles.card}>
        <Text style={globalStyles.title}>Predicción</Text>

        {predLoading ? (
          <View style={globalStyles.row}>
            <ActivityIndicator size="small" />
            <Text style={globalStyles.subtitle}>Calculando…</Text>
          </View>
        ) : prediction ? (
          <>
            <Text style={globalStyles.subtitle}>
              Resultado: {label === 1 ? "Riesgo alto" : "Riesgo bajo"}
            </Text>
            <Text style={globalStyles.subtitle}>
              Probabilidad: {proba !== null ? `${(proba * 100).toFixed(1)}%` : "—"}
            </Text>
          </>
        ) : (
          <Text style={globalStyles.subtitle}>Sin predicción aún.</Text>
        )}

        <TouchableOpacity
          style={[globalStyles.buttonPrimary, { marginTop: 10 }]}
          onPress={runPrediction}
          disabled={predLoading}
        >
          <Text style={globalStyles.buttonTextPrimary}>
            {predLoading ? "Procesando…" : "Recalcular predicción"}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}