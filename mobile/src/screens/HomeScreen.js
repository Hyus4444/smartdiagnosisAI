/*HomeScreen muestra la lista de pacientes registrados. Al cargar, hace una petición al backend para obtener los pacientes y los muestra en tarjetas. 
Cada tarjeta es clickeable y lleva a la pantalla de detalle del paciente. También incluye un botón fijo para agregar un nuevo paciente, que redirige a 
la pantalla de creación de paciente. El header tiene un botón de configuración (placeholder) para futuras funcionalidades.*/
import {
  View,
  Text,
  ActivityIndicator,
  FlatList,
  TouchableOpacity,
  Animated,
} from "react-native";
import { useLayoutEffect, useState, useCallback, useEffect, useRef } from "react";
import { useNavigation, useFocusEffect } from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";

export default function HomeScreen() {
  const navigation = useNavigation();

  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  const fadeAnim = useRef(new Animated.Value(0)).current;

  const fetchPatients = async () => {
    setLoading(true);
    try {
      const res = await api.get("/patients", {
        params: { skip: 0, limit: 50 },
      });
      setPatients(res.data.items || []);
    } catch (err) {
      console.log(
        "Error fetching patients:",
        err?.response?.status,
        err?.response?.data || err.message
      );
      setPatients([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 320,
      useNativeDriver: true,
    }).start();
  }, [fadeAnim, patients.length, loading]);

  useFocusEffect(
    useCallback(() => {
      fetchPatients();
    }, [])
  );

  useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <TouchableOpacity
          style={globalStyles.headerButton}
          onPress={() => {
            navigation.navigate("Config");
          }}
        >
          <Text style={globalStyles.headerButtonText}>⚙️</Text>
        </TouchableOpacity>
      ),
      title: "Pacientes",
    });
  }, [navigation]);

  const renderPatient = ({ item }) => (
    <Animated.View style={{ opacity: fadeAnim }}>
      <TouchableOpacity
        style={globalStyles.card}
        onPress={() => {
          navigation.navigate("PatientDetail", { patientId: item.id });
        }}
      >
        <Text style={globalStyles.name}>{item.full_name}</Text>
        <Text style={globalStyles.smallText}>
          {item.document_type} {item.document_number}
        </Text>
      </TouchableOpacity>
    </Animated.View>
  );

  return (
    <View style={globalStyles.container}>
      {loading ? (
        <ActivityIndicator size="large" color="#0A6FAE" />
      ) : patients.length === 0 ? (
        <View style={globalStyles.empty}>
          <Text style={globalStyles.mutedText}>Sin pacientes registrados</Text>
        </View>
      ) : (
        <FlatList
          data={patients}
          keyExtractor={(item) => item.id}
          renderItem={renderPatient}
          contentContainerStyle={globalStyles.list}
        />
      )}

      <TouchableOpacity
        style={globalStyles.addButton}
        onPress={() => {
          navigation.navigate("CreatePatient");
        }}
      >
        <Text style={globalStyles.buttonTextPrimary}>＋ Agregar paciente</Text>
      </TouchableOpacity>
    </View>
  );
}
