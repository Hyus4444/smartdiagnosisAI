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
