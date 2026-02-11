/*HomeScreen muestra la lista de pacientes registrados. Al cargar, hace una petición al backend para obtener los pacientes y los muestra en tarjetas. 
Cada tarjeta es clickeable y lleva a la pantalla de detalle del paciente. También incluye un botón fijo para agregar un nuevo paciente, que redirige a 
la pantalla de creación de paciente. El header tiene un botón de configuración (placeholder) para futuras funcionalidades.*/
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  FlatList,
  TouchableOpacity,
} from "react-native";
import { useEffect, useLayoutEffect, useState, useCallback} from "react";
import { useNavigation, useFocusEffect } from "@react-navigation/native";
import api from "../config/api";


export default function HomeScreen() {
  const navigation = useNavigation();

  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

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

  useFocusEffect(
  useCallback(() => {
    fetchPatients();
  }, [])
);

  // Header button (configuración de cuenta - placeholder)
  useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <TouchableOpacity
          style={styles.headerButton}
          onPress={() => {
            // futuro: navegación a configuración de cuenta
            console.log("Account settings");
          }}
        >
          <Text style={styles.headerButtonText}>⚙️</Text>
        </TouchableOpacity>
      ),
      title: "Pacientes",
    });
  }, [navigation]);

  const renderPatient = ({ item }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => {
        navigation.navigate("PatientDetail", { patientId: item.id })
      }}
    >
      <Text style={styles.name}>{item.full_name}</Text>
      <Text style={styles.document}>
        {item.document_type} {item.document_number}
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {loading ? (
        <ActivityIndicator size="large" />
      ) : patients.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>No patients registered yet</Text>
        </View>
      ) : (
        <FlatList
          data={patients}
          keyExtractor={(item) => item.id}
          renderItem={renderPatient}
          contentContainerStyle={styles.list}
        />
      )}

      {/* Botón inferior fijo */}
      <TouchableOpacity
        style={styles.addButton}
        onPress={() => {navigation.navigate("CreatePatient")
        }}
      >
        <Text style={styles.addButtonText}>＋ Add patient</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },

  list: {
    padding: 16,
    paddingBottom: 100, // espacio para el botón inferior
  },

  card: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#e0e0e0",
    marginBottom: 12,
  },

  name: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 4,
  },

  document: {
    fontSize: 13,
    color: "#666",
  },

  empty: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  emptyText: {
    fontSize: 14,
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

  headerButton: {
    marginRight: 12,
  },

  headerButtonText: {
    fontSize: 18,
  },
});
