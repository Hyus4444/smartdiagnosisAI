import { View, Text, TouchableOpacity, Animated } from "react-native";
import { useLayoutEffect, useRef, useEffect, useState } from "react";
import { useNavigation } from "@react-navigation/native";
import { globalStyles } from "../styles/globalStyles";
import AppModal from "../components/AppModal";

export default function AccountScreen() {
  const navigation = useNavigation();
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(12)).current;
  const [infoModal, setInfoModal] = useState({ visible: false, title: "", message: "" });

  useLayoutEffect(() => {
    navigation.setOptions({ title: "Configuración" });
  }, [navigation]);

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 350,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 350,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, slideAnim]);


  return (
    <View style={globalStyles.paddedContainer}>
      <Animated.View
        style={[
          globalStyles.card,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }],
          },
        ]}
      >
        <Text style={globalStyles.subtitle}>Opciones de cuenta</Text>
        <TouchableOpacity
          style={globalStyles.rowButton}
          onPress={() => navigation.navigate("Profile")}
        >
          <Text style={globalStyles.rowButtonText}>Perfil</Text>
        </TouchableOpacity>
      </Animated.View>
            <AppModal
        visible={infoModal.visible}
        title={infoModal.title}
        message={infoModal.message}
        tone="info"
        onPrimary={() => setInfoModal({ visible: false, title: "", message: "" })}
      />
    </View>
  );
}
