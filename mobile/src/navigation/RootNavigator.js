/*RootNavigator es el componente principal de navegación que decide qué pila de navegación mostrar (AuthStack o AppStack) según el estado de autenticación 
del usuario. Utiliza el contexto de autenticación para determinar si el usuario ha iniciado sesión o no, y renderiza la pila correspondiente dentro del 
contenedor de navegación de React Navigation. Esto permite una transición fluida entre las pantallas de autenticación y las pantallas principales de la aplicación, 
asegurando que los usuarios solo accedan a las funciones principales después de autenticarse correctamente.*/
import { NavigationContainer } from "@react-navigation/native";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import AuthStack from "./AuthStack";
import AppStack from "./AppStack";

export default function RootNavigator() {
  const { isAuthenticated } = useContext(AuthContext);

  return (
    <NavigationContainer>
      {isAuthenticated ? <AppStack /> : <AuthStack />}
    </NavigationContainer>
  );
}
