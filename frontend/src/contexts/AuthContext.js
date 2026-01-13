import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          const response = await axios.get(`${API}/auth/me`, {
            headers: { Authorization: `Bearer ${storedToken}` }
          });
          setUser(response.data);
          setToken(storedToken);
        } catch (error) {
          console.error('Auth initialization failed:', error);
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const signup = async (userData) => {
    try {
      const response = await axios.post(`${API}/auth/signup`, userData);
      const { access_token, user: userResponse } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userResponse);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Signup failed'
      };
    }
  };

  const login = async (credentials) => {
    try {
      const response = await axios.post(`${API}/auth/login`, credentials);
      const { access_token, user: userData } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await axios.post(`${API}/auth/logout`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
    }
  };

  const updateProfile = async (updateData) => {
    try {
      const response = await axios.put(`${API}/user/profile`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Profile update failed'
      };
    }
  };

  const deleteProfile = async () => {
    try {
      await axios.delete(`${API}/user/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Profile deletion failed'
      };
    }
  };

  const value = {
    user,
    token,
    loading,
    signup,
    login,
    logout,
    updateProfile,
    deleteProfile,
    isAuthenticated: !!token
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
