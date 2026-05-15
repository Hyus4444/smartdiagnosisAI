import {
  View,
  Text,
  ActivityIndicator,
  TouchableOpacity,
  FlatList,
  Animated
} from "react-native";
import { useState, useLayoutEffect, useCallback, useRef, useEffect } from "react";
import { useRoute, useNavigation, useFocusEffect } from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";
import AppModal from "../components/AppModal";

export default function PatientDetailScreen() {
  const route = useRoute();
  const navigation = useNavigation();
  const { patientId } = route.params;

  const [patient, setPatient] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [historyModalVisible, setHistoryModalVisible] = useState(false);

  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 280,
      useNativeDriver: true,
    }).start();
  }, [fadeAnim, loading]);

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
      const orderedRecords = (recordsRes.data?.items || [])
        .slice()
        .sort((a, b) => {
          const dateA = new Date(a.recorded_at || a.created_at || 0).getTime();
          const dateB = new Date(b.recorded_at || b.created_at || 0).getTime();
          return dateB - dateA;
        })
        .slice(0, 5);

      setRecords(orderedRecords);
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
        <ActivityIndicator size="large" color="#0A6FAE" />
      </View>
    );
  }

  if (!patient) {
    return (
      <View style={globalStyles.center}>
        <Text style={globalStyles.subtitle}>Paciente no encontrado</Text>
      </View>
    );
  }

  return (
    <Animated.View style={[globalStyles.container, { opacity: fadeAnim }]}>
      <View style={globalStyles.patientCard}>
        <Text style={globalStyles.title}>{patient.full_name}</Text>
        <Text style={globalStyles.subtitle}>
          {patient.document_type} {patient.document_number}
        </Text>
        <Text style={globalStyles.subtitle}>Fecha de nacimiento: {patient.birth_date}</Text>
        <Text style={globalStyles.subtitle}>Género: {patient.gender}</Text>
      </View>

      <View style={globalStyles.section}>
        <Text style={globalStyles.sectionTitle}>Registros clínicos recientes</Text>

        {records.length === 0 ? (
          <Text style={globalStyles.subtitle}>No hay registros aún.</Text>
        ) : (
          <FlatList data={records} keyExtractor={(item) => item.id} renderItem={renderRecord} />
        )}
      </View>

      <View style={globalStyles.footer}>
        <TouchableOpacity
          style={[globalStyles.buttonOutline, { flex: 1 }]}
          onPress={() => navigation.navigate("ClinicalRecordScreen", { patientId })}
        >
          <Text style={globalStyles.buttonTextOutline}>Ver historial</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[globalStyles.buttonPrimary, { flex: 1 }]}
          onPress={() => navigation.navigate("CreateClinicalRecord", { patientId })}
        >
          <Text style={globalStyles.buttonTextPrimary}>Añadir historial</Text>
        </TouchableOpacity>
      </View>

      <AppModal
        visible={historyModalVisible}
        title="Historial completo"
        message="La vista completa del historial estará disponible en una próxima actualización. Por ahora puedes revisar los últimos registros en esta misma pantalla."
        tone="info"
        onPrimary={() => setHistoryModalVisible(false)}
      />
    </Animated.View>
  );
}