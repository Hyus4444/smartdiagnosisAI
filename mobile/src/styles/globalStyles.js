import { StyleSheet } from "react-native";

/**
 * Estilos globales reutilizables en toda la aplicación.
 * Contiene:
 * - Layout base
 * - Tarjetas
 * - Tipografía común
 * - Botones primarios/secundarios
 * - Inputs
 */

export const globalStyles = StyleSheet.create({
  /* ===== Layout ===== */

  container: {
    flex: 1,
    backgroundColor: "#fff",
  },

  paddedContainer: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 16,
  },

  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  empty: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  list: {
    padding: 16,
    paddingBottom: 100, // espacio para el botón inferior
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderColor: "#eee",
    backgroundColor: "#fff",
  },

  /* ===== Tarjetas ===== */

  card: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#e0e0e0",
    marginBottom: 12,
  },

  patientCard: {
    backgroundColor: "#fff",
    padding: 16,
    borderBottomWidth: 1,
    borderColor: "#eee",
  },

  borderedSection: {
    backgroundColor: "#fff",
    padding: 16,
    borderBottomWidth: 1,
    borderColor: "#eee",
  },

  /* ===== Tipografía ===== */

  title: {
    fontSize: 18,
    fontWeight: "600",
  },

  subtitle: {
    fontSize: 16,
    fontWeight: "600",
  },

  label: {
    fontSize: 12,
    color: "#666",
    marginBottom: 6,
  },

  text: {
    fontSize: 14,
    color: "#000",
  },

  smallText: {
    fontSize: 13,
    color: "#666",
  },

  mutedText: {
    fontSize: 12,
    color: "#555",
  },

  name: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 4,
  },

  /* ===== Filas ===== */

  row: {
    flexDirection: "row",
    marginBottom: 8,
    gap: 12,
  },

  rowBetween: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  rowButton: {
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: "#eee",
  },

  /* ===== Inputs ===== */

  input: {
    borderWidth: 1,
    borderColor: "#e0e0e0",
    borderRadius: 10,
    padding: 12,
    fontSize: 14,
    marginBottom: 12,
    backgroundColor: "#fff",
  },

  textarea: {
    borderWidth: 1,
    borderColor: "#e0e0e0",
    borderRadius: 10,
    padding: 12,
    fontSize: 14,
    minHeight: 120,
    textAlignVertical: "top",
    backgroundColor: "#fff",
    marginBottom: 12,
  },

  /* ===== Botones ===== */

  buttonPrimary: {
    backgroundColor: "#006496",
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
  },

  buttonSecondary: {
    backgroundColor: "#000",
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
  },

  addButton: {
    position: "absolute",
    bottom: 20,
    left: 20,
    right: 20,
    backgroundColor: "#006496",
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
  },

  buttonOutline: {
    borderWidth: 1,
    borderColor: "#000",
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
  },

  buttonTextPrimary: {
    color: "#fff",
    fontSize: 14,
    fontWeight: "600",
  },

  buttonTextOutline: {
    color: "#000",
    fontSize: 14,
    fontWeight: "600",
  },

  headerButton: {
    marginRight: 12,
  },

  headerButtonText: {
    fontSize: 18,
  },
  /* ===== Botones flotantes inferiores ===== */

  footer: {
    position: "absolute",
    bottom: 20,
    left: 20,
    right: 20,
    flexDirection: "row",
    gap: 12,
  },

  bottomActionsColumn: {
    position: "absolute",
    bottom: 20,
    left: 20,
    right: 20,
    flexDirection: "column",
    gap: 10,
  },

  /* ===== Listas ===== */

  listItem: {
    backgroundColor: "#fff",
    padding: 14,
    borderBottomWidth: 1,
    borderColor: "#eee",
  },

  divider: {
    height: 1,
    backgroundColor: "#eee",
  },
});
