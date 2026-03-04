import {
  View,
  Text,
  ActivityIndicator,
  TouchableOpacity,
  FlatList,
} from "react-native";
import { useState, useLayoutEffect, useCallback } from "react";
import { useRoute, useNavigation, useFocusEffect } from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";

export default function PatientDetailScreen() {
  const route = useRoute();
  const navigation = useNavigation();
  const { patientId } = route.params;

  const [patient, setPatient] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [patientRes, recordsRes] = await Promise.all([
        api.get(`/patients/${patientId}`),
        api.get(`/patients/${patientId}/clinical-records`, {
          params: { skip: 0, limit: 10 },
        }),
      ]);

      setPatient(patientRes.data);
      setRecords(recordsRes.data?.items || []);
    } catch (err) {
      console.log(
        "Error detalle paciente:",
        err?.response?.status,
        err?.response?.data || err.message
      );
      setPatient(null);
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchData();
    }, [patientId])
  );

  useLayoutEffect(() => {
    navigation.setOptions({
      title: "Detalle del paciente",
    });
  }, [navigation]);

  const renderRecord = ({ item }) => {
    const dateLabel = item.recorded_at
      ? new Date(item.recorded_at).toLocaleString()
      : item.created_at
      ? new Date(item.created_at).toLocaleString()
      : "Sin fecha";

    return (
      <TouchableOpacity
        style={globalStyles.listItem}
        onPress={() =>
          navigation.navigate("ClinicalRecordDetail", {
            patientId,
            recordId: item.id,
          })
        }
      >
        <Text style={globalStyles.listItemTitle}>{dateLabel}</Text>
        <Text style={globalStyles.listItemSubtitle}>
          Glucosa: {item.blood_glucose_level} | HbA1c: {item.hba1c_level}
        </Text>
      </TouchableOpacity>
    );
  };

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

      {/* Lista corta de registros clínicos (últimos 10) */}
      <View style={globalStyles.section}>
        <Text style={globalStyles.sectionTitle}>Registros clínicos recientes</Text>

        {records.length === 0 ? (
          <Text style={globalStyles.subtitle}>No hay registros aún.</Text>
        ) : (
          <FlatList
            data={records}
            keyExtractor={(item) => item.id}
            renderItem={renderRecord}
          />
        )}
      </View>

      {/* Acciones inferiores */}
      <View style={globalStyles.footer}>
        <TouchableOpacity
          style={[
            globalStyles.buttonPrimary,
            globalStyles.buttonSecondary,
            { flex: 1 },
          ]}
          onPress={() => navigation.navigate("ClinicalRecordsList", { patientId })}
        >
          <Text style={globalStyles.buttonTextPrimary}>Ver historial</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[globalStyles.buttonPrimary, { flex: 1 }]}
          onPress={() => navigation.navigate("CreateClinicalRecord", { patientId })}
        >
          <Text style={globalStyles.buttonTextPrimary}>Añadir historial</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}