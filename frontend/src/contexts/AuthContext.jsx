import { createContext, useContext, useEffect, useState } from "react";

import { authApi } from "../services/api.js";
import { storage } from "../services/storage.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(storage.getToken());
  const [user, setUser] = useState(storage.getUser());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function bootstrap() {
      const savedToken = storage.getToken();
      if (!savedToken) {
        setIsLoading(false);
        return;
      }
      try {
        const profile = await authApi.me(savedToken);
        setToken(savedToken);
        setUser(profile);
        storage.setUser(profile);
      } catch (error) {
        storage.clearToken();
        storage.clearUser();
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    bootstrap();
  }, []);

  async function login(credentials) {
    const payload = await authApi.login(credentials);
    storage.setToken(payload.access_token);
    storage.setUser(payload.user);
    setToken(payload.access_token);
    setUser(payload.user);
    return payload;
  }

  function logout() {
    storage.clearToken();
    storage.clearUser();
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isLoading,
        isAuthenticated: Boolean(token && user),
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
