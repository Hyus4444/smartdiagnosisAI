import api from "../config/api";

export const login = async (email, password) => {
  try {
    const response = await api.post("/auth/login", {
      email,
      password,
    });

    return response.data;
  } catch (error) {
    console.error(
      "Login error:",
      error.response?.data || error.message
    );
    throw error;
  }
};

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
