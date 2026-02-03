import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Button,
} from "react-native";
import { useContext, useEffect, useState } from "react";
import api from "../config/api";
import { AuthContext } from "../context/AuthContext";

export default function HomeScreen() {
  const { token, logout } = useContext(AuthContext);
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = async () => {
    setLoading(true);
    try {
      const res = await api.get("/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMe(res.data);
    } catch (err) {
      console.log("Error /auth/me:", err?.response?.data || err.message);
      setMe(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMe();
  }, []);

  return (
    <View style={styles.container}>
      {loading ? (
        <ActivityIndicator size="large" />
      ) : me ? (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Usuario autenticado</Text>

          <View style={styles.row}>
            <Text style={styles.label}>ID:</Text>
            <Text style={styles.value}>{String(me.id)}</Text>
          </View>

          <View style={styles.row}>
            <Text style={styles.label}>Email:</Text>
            <Text style={styles.value}>{me.email}</Text>
          </View>

          <View style={styles.row}>
            <Text style={styles.label}>Nombre:</Text>
            <Text style={styles.value}>{me.full_name}</Text>
          </View>
        </View>
      ) : (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>No se pudo obtener /auth/me</Text>
          <Text style={styles.value}>
            Verifica que el endpoint exista y que el token sea válido.
          </Text>
        </View>
      )}

      <View style={styles.actions}>
        <Button title="Refrescar" onPress={fetchMe} />
        <View style={{ height: 10 }} />
        <Button title="Cerrar sesión" onPress={logout} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, gap: 12 },
  title: { fontSize: 22, fontWeight: "600" },
  card: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#ddd",
    backgroundColor: "#fff",
  },
  cardTitle: { fontSize: 16, fontWeight: "600", marginBottom: 10 },
  row: { marginBottom: 8 },
  label: { fontSize: 12, color: "#666" },
  value: { fontSize: 14 },
  actions: { marginTop: 10 },
});
