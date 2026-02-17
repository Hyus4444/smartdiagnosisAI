import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  FlatList,
  TouchableOpacity,
} from "react-native";
import { useCallback, useLayoutEffect, useState } from "react";
import { useFocusEffect, useNavigation, useRoute } from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";

export default function ClinicalRecordsListScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { patientId } = route.params;

  const [records, setRecords] = useState([]);
  const [patientName, setPatientName] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      // Traemos nombre del paciente (opcional) + records
      const [patientRes, recordsRes] = await Promise.all([
        api.get(`/patients/${patientId}`),
        api.get(`/patients/${patientId}/clinical-records`, {
          params: { skip: 0, limit: 50 },
        }),
      ]);

      setPatientName(patientRes.data?.full_name ?? null);
      setRecords(recordsRes.data?.items || []);
    } catch (err) {
      console.log(
        "Error listando historiales:",
        err?.response?.status,
        err?.response?.data || err.message
      );
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchRecords();
    }, [patientId])
  );

  useLayoutEffect(() => {
    navigation.setOptions({
      title: "Historial clínico",
    });
  }, [navigation]);

  const renderItem = ({ item }) => {
    const dateLabel = item?.created_at
      ? new Date(item.created_at).toLocaleString()
      : "Sin fecha";

    return (
      <View style={globalStyles.card}>
        <Text style={globalStyles.date}>{dateLabel}</Text>
        <Text style={globalStyles.content}>{item.content}</Text>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={globalStyles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={globalStyles.container}>
      {patientName ? (
        <View style={globalStyles.header}>
          <Text style={globalStyles.title}>{patientName}</Text>
        </View>
      ) : null}

      {records.length === 0 ? (
        <View style={globalStyles.center}>
          <Text style={globalStyles.emptyText}>No hay registros clínicos aún.</Text>
        </View>
      ) : (
        <FlatList
          data={records}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={globalStyles.list}
        />
      )}

      <View style={globalStyles.footer}>
        <TouchableOpacity
          style={[globalStyles.buttonPrimary, globalStyles.buttonSecondary, { flex: 1 }]}
          onPress={fetchRecords}
        >
          <Text style={globalStyles.buttonTextPrimary}>Actualizar</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[globalStyles.buttonPrimary, { flex: 1 }]}
          onPress={() => navigation.navigate("CreateClinicalRecord", { patientId })}
        >
          <Text style={globalStyles.buttonTextPrimary}>Añadir</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
