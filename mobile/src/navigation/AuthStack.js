/*Define la pila de navegación para la autenticación, incluyendo las pantallas de inicio de sesión y registro. Utiliza el stack navigator de React Navigation para 
manejar la navegación entre estas pantallas. Esta pila se muestra a los usuarios que no han iniciado sesión, permitiéndoles acceder a las funciones de autenticación 
antes de ingresar a la aplicación principal.*/
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import LoginScreen from "../screens/LoginScreen";
import RegisterScreen from "../screens/RegisterScreen";

const Stack = createNativeStackNavigator();

export default function AuthStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="Login"
        component={LoginScreen}
        options={{ title: "Iniciar Sesión" }}
      />
      <Stack.Screen
        name="Register"
        component={RegisterScreen}
        options={{ title: "Registro" }}
      />
    </Stack.Navigator>
  );
}
