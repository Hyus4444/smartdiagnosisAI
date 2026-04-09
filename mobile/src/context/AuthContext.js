/*Contexto de autenticación para manejar el estado de autenticación en la aplicación. Proporciona funciones para iniciar sesión, registrarse y cerrar sesión, 
así como el estado de carga y el token de autenticación. Este contexto se utiliza para compartir la información de autenticación en toda la aplicación y controlar 
el acceso a las pantallas protegidas.*/
import React, { createContext, useState } from "react";
import * as authService from "../services/authService";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const loadProfile = async () => {
    try {
      const me = await authService.getMe();
      setUser(me);
      return me;
    } catch (_) {
      setUser(null);
      return null;
    }
  };

  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const nextToken = await authService.login(email, password);
      setToken(nextToken);
      await loadProfile();
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
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isLoading,
        login,
        register,
        logout,
        refreshUser: loadProfile,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
