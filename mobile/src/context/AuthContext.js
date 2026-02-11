/*Contexto de autenticación para manejar el estado de autenticación en la aplicación. Proporciona funciones para iniciar sesión, registrarse y cerrar sesión, 
así como el estado de carga y el token de autenticación. Este contexto se utiliza para compartir la información de autenticación en toda la aplicación y controlar 
el acceso a las pantallas protegidas.*/
import React, { createContext, useState } from "react";
import * as authService from "../services/authService";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const token = await authService.login(email, password);
      setToken(token);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData) => {
    setIsLoading(true);
    try {
      await authService.register(userData);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        isLoading,
        login,
        register,
        logout,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
