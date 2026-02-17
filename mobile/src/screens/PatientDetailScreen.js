import {
  View,
  Text,
  ActivityIndicator,
  TouchableOpacity,
} from "react-native";
import { useState, useLayoutEffect, useCallback } from "react";
import {
  useRoute,
  useNavigation,
  useFocusEffect,
} from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";

export default function PatientDetailScreen() {
  const route = useRoute();
  const navigation = useNavigation();
  const { patientId } = route.params;

  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const patientRes = await api.get(`/patients/${patientId}`);
      setPatient(patientRes.data);
    } catch (err) {
      console.log(
        "Error detalle paciente:",
        err?.response?.status,
        err?.response?.data || err.message,
      );
      setPatient(null);
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchData();
    }, [patientId]),
  );

  useLayoutEffect(() => {
    navigation.setOptions({
      title: "Detalle del paciente",
    });
  }, [navigation]);

  if (loading) {
    return (
      <View style={globalStyles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (!patient) {
    return (
      <View style={globalStyles.center}>
        <Text>Paciente no encontrado</Text>
      </View>
    );
  }

  return (
    <View style={globalStyles.container}>
      {/* Información del paciente */}
      <View style={globalStyles.patientCard}>
        <Text style={globalStyles.title}>{patient.full_name}</Text>
        <Text style={globalStyles.subtitle}>
          {patient.document_type} {patient.document_number}
        </Text>
        <Text style={globalStyles.subtitle}>
          Fecha de nacimiento: {patient.birth_date}
        </Text>
        <Text style={globalStyles.subtitle}>Género: {patient.gender}</Text>
      </View>

      {/* Acciones inferiores */}
      <View style={globalStyles.footer}>
        <TouchableOpacity
          style={[globalStyles.buttonPrimary, globalStyles.buttonSecondary, { flex: 1 }]}
          onPress={() =>
            navigation.navigate("ClinicalRecordsList", { patientId })
          }
        >
          <Text style={globalStyles.buttonTextPrimary}>Ver historial</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[globalStyles.buttonPrimary, { flex: 1 }]}
          onPress={() =>
            navigation.navigate("CreateClinicalRecord", { patientId })
          }
        >
          <Text style={globalStyles.buttonTextPrimary}>Añadir historial</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}