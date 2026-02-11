/*Documento para manejar la autenticación, incluyendo login y registro de usuarios. Utiliza SecureStore para almacenar el token de acceso de forma segura en el dispositivo 
móvil.*/
import api from "../config/api";
import * as SecureStore from "expo-secure-store";

export async function login(email, password) {
  const body = new URLSearchParams();
  body.append("username", email); 
  body.append("password", password); 

  const res = await api.post("/auth/login", body.toString(), {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  const { access_token } = res.data;

  await SecureStore.setItemAsync("access_token", access_token);
  return access_token;
}


export const register = async (userData) => {
  try {
    const response = await api.post("/auth/register", userData);
    return response.data;
  } catch (error) {
    console.error(
      "Register error:",
      error.response?.data || error.message
    );
    throw error;
  }
};
