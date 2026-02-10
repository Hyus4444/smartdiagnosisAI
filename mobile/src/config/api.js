import axios from "axios";

const API_BASE_URL = "http://192.168.1.2:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 5000,
});

export default api;