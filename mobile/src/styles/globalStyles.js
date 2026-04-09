import { StyleSheet } from "react-native";

const COLORS = {
  background: "#F4F8FB",
  surface: "#FFFFFF",
  border: "#D6E2EA",
  primary: "#0A6FAE",
  primaryDark: "#095B8E",
  accent: "#0FA3B1",
  text: "#102A43",
  muted: "#627D98",
  danger: "#C0392B",
};

export const globalStyles = StyleSheet.create({
  /* ===== Layout ===== */
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },

  paddedContainer: {
    flex: 1,
    backgroundColor: COLORS.background,
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
    paddingBottom: 100,
  },

  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surface,
  },

  /* ===== Tarjetas ===== */
  card: {
    backgroundColor: COLORS.surface,
    padding: 16,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 12,
    shadowColor: "#0B2942",
    shadowOpacity: 0.08,
    shadowOffset: { width: 0, height: 3 },
    shadowRadius: 8,
    elevation: 2,
  },

  patientCard: {
    backgroundColor: COLORS.surface,
    padding: 16,
    borderBottomWidth: 1,
    borderColor: COLORS.border,
  },

  borderedSection: {
    backgroundColor: COLORS.surface,
    padding: 16,
    borderBottomWidth: 1,
    borderColor: COLORS.border,
  },

  /* ===== Tipografía ===== */
  title: {
    fontSize: 20,
    fontWeight: "700",
    color: COLORS.text,
  },

  subtitle: {
    fontSize: 16,
    fontWeight: "600",
    color: COLORS.text,
  },

  label: {
    fontSize: 12,
    color: COLORS.muted,
    marginBottom: 6,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },

  text: {
    fontSize: 15,
    color: COLORS.text,
  },

  smallText: {
    fontSize: 13,
    color: COLORS.muted,
  },

  mutedText: {
    fontSize: 13,
    color: COLORS.muted,
  },

  name: {
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 4,
    color: COLORS.text,
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
    paddingVertical: 14,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },

  rowButtonText: {
    fontSize: 15,
    fontWeight: "600",
    color: COLORS.text,
  },

  /* ===== Inputs ===== */
  input: {
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    padding: 12,
    fontSize: 14,
    marginBottom: 12,
    backgroundColor: COLORS.surface,
    color: COLORS.text,
  },

  textarea: {
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    padding: 12,
    fontSize: 14,
    minHeight: 120,
    textAlignVertical: "top",
    backgroundColor: COLORS.surface,
    marginBottom: 12,
    color: COLORS.text,
  },

  /* ===== Botones ===== */
  buttonPrimary: {
    backgroundColor: COLORS.primary,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },

  buttonSecondary: {
    backgroundColor: COLORS.danger,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },

  addButton: {
    position: "absolute",
    bottom: 20,
    left: 20,
    right: 20,
    backgroundColor: COLORS.primary,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    shadowColor: "#093D5D",
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 6 },
    shadowRadius: 12,
    elevation: 3,
  },

  buttonOutline: {
    borderWidth: 1,
    borderColor: COLORS.primaryDark,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },

  buttonTextPrimary: {
    color: "#fff",
    fontSize: 14,
    fontWeight: "700",
  },

  buttonTextOutline: {
    color: COLORS.primaryDark,
    fontSize: 14,
    fontWeight: "700",
  },

  headerButton: {
    marginRight: 12,
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#E5F1F8",
  },

  headerButtonText: {
    fontSize: 16,
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
    backgroundColor: COLORS.surface,
    padding: 14,
    borderBottomWidth: 1,
    borderColor: COLORS.border,
  },

  divider: {
    height: 1,
    backgroundColor: COLORS.border,
  },

  /* ===== Config / Perfil ===== */
  sectionSpacing: {
    marginTop: 18,
  },

  heroCard: {
    backgroundColor: COLORS.primary,
    borderRadius: 14,
    padding: 18,
    marginBottom: 14,
  },

  heroTitle: {
    color: "#FFFFFF",
    fontSize: 18,
    fontWeight: "700",
  },

  heroText: {
    color: "#DAECF8",
    marginTop: 6,
    fontSize: 13,
  },

  profileAvatar: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: "#DBEEF9",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 12,
  },

  profileAvatarText: {
    fontSize: 24,
    fontWeight: "700",
    color: COLORS.primaryDark,
  },

  profileValue: {
    fontSize: 15,
    color: COLORS.text,
    marginBottom: 10,
  },
});
