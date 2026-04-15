/*Pantalla para crear un nuevo paciente, con campos para el nombre completo, tipo y número de documento, fecha de nacimiento y género. Incluye validación de campos 
y manejo de errores al enviar la información al backend. Al guardar, redirige a la pantalla de inicio para que se actualice la lista de pacientes.*/
import { useState, useRef, useEffect } from "react";
import { View, Text, TextInput, TouchableOpacity, Animated } from "react-native";
import { useNavigation } from "@react-navigation/native";
import api from "../config/api";
import { globalStyles } from "../styles/globalStyles";
import AppModal from "../components/AppModal";

export default function CreatePatientScreen() {
  const navigation = useNavigation();
  const [fullName, setFullName] = useState("");
  const [documentType, setDocumentType] = useState("CC");
  const [documentNumber, setDocumentNumber] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [gender, setGender] = useState("M");
  const [loading, setLoading] = useState(false);
  const [modalData, setModalData] = useState({ visible: false, title: "", message: "", tone: "info" });
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

  const validate = () => {
    if (!fullName.trim()) return "El nombre completo es obligatorio.";
    if (!documentType.trim()) return "El tipo de documento es obligatorio.";
    if (!documentNumber.trim()) return "El número de documento es obligatorio.";
    if (!birthDate.trim()) return "La fecha de nacimiento es obligatoria (YYYY-MM-DD).";
    if (!/^\d{4}-\d{2}-\d{2}$/.test(birthDate.trim())) {
      return "El formato de la fecha de nacimiento debe ser YYYY-MM-DD.";
    }
    if (!gender.trim()) return "El género es obligatorio.";
    return null;
  };

  const handleCreate = async () => {
    const errMsg = validate();
    if (errMsg) {
      openModal("Validación", errMsg, "error");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        full_name: fullName.trim(),
        document_type: documentType.trim().toUpperCase(),
        document_number: documentNumber.trim(),
        birth_date: birthDate.trim(),
        gender: gender.trim().toUpperCase(),
      };

      await api.post("/patients", payload);

      navigation.navigate("Home", { refresh: Date.now() });
    } catch (err) {
      const status = err?.response?.status;
      const data = err?.response?.data;

      if (status === 409) {
        openModal("Duplicado", data?.detail || "El paciente ya existe.", "error");
      } else if (status === 422) {
        openModal("Validación", "Campos inválidos. Revisa los valores e intenta de nuevo.", "error");
      } else if (status === 401) {
        openModal("Sesión", "No autorizado. Inicia sesión nuevamente.", "error");
      } else {
        openModal("Error", data?.detail || err.message, "error");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={globalStyles.container}>
      <Animated.View style={[globalStyles.paddedContainer, { opacity: fadeAnim }]}>
        <View style={{ marginBottom: 12 }}>
          <Text style={globalStyles.label}>Nombre completo</Text>
          <TextInput
            style={globalStyles.input}
            value={fullName}
            onChangeText={setFullName}
            placeholder="Ej: María López"
            autoCapitalize="words"
          />
        </View>
        <View style={globalStyles.row}>
          <View style={{ flex: 1, marginBottom: 12 }}>
            <Text style={globalStyles.label}>Tipo de documento</Text>
            <TextInput
              style={globalStyles.input}
              value={documentType}
              onChangeText={setDocumentType}
              placeholder="CC"
              autoCapitalize="characters"
            />
          </View>

          <View style={{ flex: 2, marginBottom: 12 }}>
            <Text style={globalStyles.label}>Número de documento</Text>
            <TextInput
              style={globalStyles.input}
              value={documentNumber}
              onChangeText={setDocumentNumber}
              placeholder="Ej: 987654321"
              keyboardType="default"
            />
          </View>
        </View>

        <View style={globalStyles.row}>
          <View style={{ flex: 1, marginBottom: 12 }}>
            <Text style={globalStyles.label}>Fecha de nacimiento</Text>
            <TextInput
              style={globalStyles.input}
              value={birthDate}
              onChangeText={setBirthDate}
              placeholder="YYYY-MM-DD"
            />
          </View>

          <View style={{ flex: 1, marginBottom: 12 }}>
            <Text style={globalStyles.label}>Género</Text>
            <TextInput
              style={globalStyles.input}
              value={gender}
              onChangeText={setGender}
              placeholder="M / F"
              autoCapitalize="characters"
            />
          </View>
        </View>
      </Animated.View>
      <View style={globalStyles.footer}>
        <TouchableOpacity
          style={[globalStyles.buttonOutline, { marginTop: 8, flex: 1 }]}
          onPress={() => navigation.goBack()}
        >
          <Text style={globalStyles.buttonTextOutline}>Cancelar</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[globalStyles.buttonPrimary, { marginTop: 8, flex: 1 }]}
          onPress={handleCreate}
        >
          <Text style={globalStyles.buttonTextPrimary}>{loading ? "Guardando..." : "Guardar"}</Text>
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
