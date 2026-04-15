import { Modal, View, Text, TouchableOpacity } from "react-native";
import { globalStyles } from "../styles/globalStyles";

export default function AppModal({
  visible,
  title,
  message,
  primaryLabel = "Aceptar",
  onPrimary,
  secondaryLabel,
  onSecondary,
  tone = "info",
}) {
  const toneStyle =
    tone === "error"
      ? globalStyles.modalToneError
      : tone === "success"
      ? globalStyles.modalToneSuccess
      : globalStyles.modalToneInfo;

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onPrimary}>
      <View style={globalStyles.modalBackdrop}>
        <View style={globalStyles.modalCard}>
          <View style={[globalStyles.modalTone, toneStyle]} />
          <Text style={globalStyles.modalTitle}>{title}</Text>
          <Text style={globalStyles.modalMessage}>{message}</Text>

          <View style={globalStyles.modalActions}>
            {secondaryLabel ? (
              <TouchableOpacity
                style={[globalStyles.buttonOutline, { flex: 1 }]}
                onPress={onSecondary}
              >
                <Text style={globalStyles.buttonTextOutline}>{secondaryLabel}</Text>
              </TouchableOpacity>
            ) : null}
            <TouchableOpacity
              style={[globalStyles.buttonPrimary, { flex: 1 }]}
              onPress={onPrimary}
            >
              <Text style={globalStyles.buttonTextPrimary}>{primaryLabel}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}
