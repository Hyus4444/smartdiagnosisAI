import React, { createContext, useState } from "react";
import * as authService from "../services/authService";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const data = await authService.login(email, password);
      setToken(data.access_token);
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
