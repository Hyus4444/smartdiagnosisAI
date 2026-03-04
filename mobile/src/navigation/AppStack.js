/*Navegacion interna de la aplicación, define las pantallas y su orden en la pila de navegación. Incluye la pantalla de inicio, la pantalla para crear un nuevo paciente 
y la pantalla de detalles del paciente. Utiliza el stack navigator de React Navigation para manejar la navegación entre estas pantallas.*/
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import HomeScreen from "../screens/HomeScreen";
import CreatePatientScreen from "../screens/CreatePatientScreen";
import PatientDetailScreen from "../screens/PatientDetailScreen";
import CreateClinicalRecordScreen from "../screens/CreateClinicalRecordScreen";
import AccountScreen from "../screens/ConfigScreen";
import ClinicalRecordDetailScreen from "../screens/ClinicalRecordDetailScreen";

const Stack = createNativeStackNavigator();

export default function AppStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="Home"
        component={HomeScreen}
        options={{ title: "SmartDiagnosis AI" }}
      />
      <Stack.Screen
        name="CreatePatient"
        component={CreatePatientScreen}
        options={{ title: "Crear Paciente" }}
      />
      <Stack.Screen
        name="PatientDetail"
        component={PatientDetailScreen}
        options={{ title: "Detalle del Paciente" }}
      />
      <Stack.Screen
        name="CreateClinicalRecord"
        component={CreateClinicalRecordScreen}
        options={{ title: "Agregar Registro Clínico" }}
      />
      <Stack.Screen
        name="Config"
        component={AccountScreen}
        options={{ title: "Configuración" }}
      />
      <Stack.Screen
        name="ClinicalRecordDetail"
        component={ClinicalRecordDetailScreen}
        options={{ title: "Registro Clínico" }}
      />
    </Stack.Navigator>
  );
}
