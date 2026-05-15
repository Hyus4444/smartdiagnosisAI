import {
  View,
  Text,
  ActivityIndicator,
  FlatList,
  TouchableOpacity,
  Animated,
} from "react-native";
import { useCallback, useEffect, useRef, useState, useLayoutEffect } from "react";
import { useNavigation, useRoute, useFocusEffect } from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";
import AppModal from "../components/AppModal";

export default function ClinicalRecordsListScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { patientId, patientName: patientNameFromParams } = route.params;

  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [records, setRecords] = useState([]);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [patientName, setPatientName] = useState(patientNameFromParams || "Paciente");

  const [modalData, setModalData] = useState({
    visible: false,
    title: "",
    message: "",
    tone: "info",
  });

  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 280,
      useNativeDriver: true,
    }).start();
  }, [fadeAnim, loading]);

  const openModal = (title, message, tone = "info") => {
    setModalData({ visible: true, title, message, tone });
  };


  const fetchPatientName = async () => {
    if (patientNameFromParams) {
      setPatientName(patientNameFromParams);
      return;
    }

    try {
      const res = await api.get(`/patients/${patientId}`);
      setPatientName(res.data?.full_name || "Paciente");
    } catch (_) {
      setPatientName("Paciente");
    }
  };

  const fetchRecords = async (isLoadMore = false) => {
    if (isLoadMore) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }

    try {
      const currentSkip = isLoadMore ? skip : 0;
      const limit = 15;

      const res = await api.get(`/patients/${patientId}/clinical-records`, {
        params: { skip: currentSkip, limit },
      });

      const nextItems = res.data?.items || [];

      if (isLoadMore) {
        setRecords((prev) => [...prev, ...nextItems]);
      } else {
        setRecords(nextItems);
      }

      setSkip(currentSkip + nextItems.length);
      setHasMore(nextItems.length === limit);
    } catch (err) {
      const payload = err?.response?.data;
      openModal(
        "Error al cargar historial",
        payload?.detail || "No se pudieron obtener los registros clínicos.",
        "error"
      );
    } finally {
      if (isLoadMore) {
        setLoadingMore(false);
      } else {
        setLoading(false);
      }
    }
  };

  useFocusEffect(
    useCallback(() => {
      setSkip(0);
      setHasMore(true);
      fetchPatientName();
      fetchRecords(false);
    }, [patientId, patientNameFromParams])
  );

  const handleRecordPress = (record) => {
    navigation.navigate("ClinicalRecordDetail", {
      patientId,
      recordId: record.id,
    });
  };


  useLayoutEffect(() => {
    navigation.setOptions({ title: patientName });
  }, [navigation, patientName]);

  const renderRecord = ({ item }) => {
    const dateLabel = item.recorded_at
      ? new Date(item.recorded_at).toLocaleString()
      : item.created_at
      ? new Date(item.created_at).toLocaleString()
      : "Sin fecha";

    return (
      <TouchableOpacity style={globalStyles.listItem} onPress={() => handleRecordPress(item)}>
        <Text style={globalStyles.listItemTitle}>{dateLabel}</Text>
        <Text style={globalStyles.listItemSubtitle}>
          Glucosa: {item.blood_glucose_level} · HbA1c: {item.hba1c_level}
        </Text>
        <Text style={globalStyles.listItemSubtitle}>
          Presión: {item.systolic_bp}/{item.diastolic_bp} · IMC: {item.bmi ?? "—"}
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

  return (
    <View style={globalStyles.container}>
      <Animated.View style={{ flex: 1, opacity: fadeAnim }}>

        {records.length === 0 ? (
          <View style={globalStyles.empty}>
            <Text style={globalStyles.subtitle}>No hay registros clínicos aún.</Text>
          </View>
        ) : (
          <FlatList
            data={records}
            keyExtractor={(item) => item.id}
            renderItem={renderRecord}
            contentContainerStyle={{ paddingBottom: 90 }}
            ItemSeparatorComponent={() => <View style={globalStyles.divider} />}
            onEndReachedThreshold={0.4}
            onEndReached={() => {
              if (!loadingMore && hasMore) {
                fetchRecords(true);
              }
            }}
            ListFooterComponent={
              loadingMore ? (
                <View style={{ paddingVertical: 14 }}>
                  <ActivityIndicator size="small" color="#0A6FAE" />
                </View>
              ) : null
            }
          />
        )}

        <View style={globalStyles.footer}>
          <TouchableOpacity
            style={[globalStyles.buttonOutline, { flex: 1 }]}
            onPress={() => navigation.goBack()}
          >
            <Text style={globalStyles.buttonTextOutline}>Volver</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[globalStyles.buttonPrimary, { flex: 1 }]}
            onPress={() => navigation.navigate("CreateClinicalRecord", { patientId, patientName })}
          >
            <Text style={globalStyles.buttonTextPrimary}>Nuevo registro</Text>
          </TouchableOpacity>
        </View>
      </Animated.View>

      <AppModal
        visible={modalData.visible}
        title={modalData.title}
        message={modalData.message}
        tone={modalData.tone}
        onPrimary={() =>
          setModalData({ visible: false, title: "", message: "", tone: "info" })
        }
      />
    </View>
  );
}