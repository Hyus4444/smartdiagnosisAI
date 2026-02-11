/*PatientDetailScreen muestra la información detallada de un paciente seleccionado, incluyendo su nombre completo, tipo y número de documento, 
fecha de nacimiento, género y una lista de sus registros clínicos. Al cargar, hace peticiones al backend para obtener la información del paciente 
y sus registros clínicos. Cada registro clínico se muestra con su fecha de creación y contenido. También incluye un botón para agregar un nuevo registro 
clínico, que redirige a la pantalla de creación de registro clínico para ese paciente.*/
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  FlatList,
  TouchableOpacity,
} from "react-native";
import { useState, useLayoutEffect, useCallback } from "react";
import { useRoute, useNavigation, useFocusEffect } from "@react-navigation/native";
import api from "../config/api";

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
          params: { skip: 0, limit: 50 },
        }),
      ]);

      setPatient(patientRes.data);
      setRecords(recordsRes.data.items || []);
    } catch (err) {
      console.log(
        "Patient detail error:",
        err?.response?.status,
        err?.response?.data || err.message
      );
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
      title: "Patient detail",
    });
  }, [navigation]);

  const renderRecord = ({ item }) => (
    <View style={styles.recordCard}>
      <Text style={styles.recordDate}>
        {new Date(item.created_at).toLocaleDateString()}
      </Text>
      <Text style={styles.recordText}>{item.content}</Text>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (!patient) {
    return (
      <View style={styles.center}>
        <Text>Patient not found</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Patient info */}
      <View style={styles.patientCard}>
        <Text style={styles.name}>{patient.full_name}</Text>
        <Text style={styles.document}>
          {patient.document_type} {patient.document_number}
        </Text>
        <Text style={styles.meta}>
          Birth date: {patient.birth_date}
        </Text>
        <Text style={styles.meta}>Gender: {patient.gender}</Text>
      </View>

      {/* Clinical records */}
      <Text style={styles.sectionTitle}>Clinical records</Text>

      {records.length === 0 ? (
        <Text style={styles.emptyText}>No clinical records yet</Text>
      ) : (
        <FlatList
          data={records}
          keyExtractor={(item) => item.id}
          renderItem={renderRecord}
          contentContainerStyle={{ paddingBottom: 100 }}
        />
      )}

      {/* Add record button */}
      <TouchableOpacity
        style={styles.addButton}
        onPress={() =>
          navigation.navigate("CreateClinicalRecord", { patientId })
        }
      >
        <Text style={styles.addButtonText}>＋ Add clinical record</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },

  patientCard: {
    backgroundColor: "#fff",
    padding: 16,
    borderBottomWidth: 1,
    borderColor: "#eee",
  },

  name: { fontSize: 18, fontWeight: "600", marginBottom: 4 },
  document: { fontSize: 14, color: "#555", marginBottom: 6 },
  meta: { fontSize: 13, color: "#666" },

  sectionTitle: {
    fontSize: 14,
    fontWeight: "600",
    marginTop: 12,
    marginBottom: 6,
    paddingHorizontal: 16,
  },

  recordCard: {
    backgroundColor: "#fff",
    padding: 14,
    borderBottomWidth: 1,
    borderColor: "#eee",
  },

  recordDate: { fontSize: 12, color: "#666", marginBottom: 4 },
  recordText: { fontSize: 14 },

  emptyText: {
    padding: 16,
    fontSize: 13,
    color: "#666",
  },

  addButton: {
    position: "absolute",
    bottom: 20,
    left: 20,
    right: 20,
    backgroundColor: "#000",
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
  },

  addButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
});
