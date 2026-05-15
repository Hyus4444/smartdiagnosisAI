/*Documento de configuracion de la instancia de axios para realizar las peticiones a la API del backend. Se establece la URL base del backend y se configura un interceptor 
para agregar el token de autenticación a cada solicitud si está disponible en el almacenamiento seguro.*/
import axios from "axios";
import * as SecureStore from "expo-secure-store";

const api = axios.create({
  baseURL: "http://192.168.1.11:8000", 
  timeout: 15000,
});

api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync("access_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
