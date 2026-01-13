import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return { Authorization: `Bearer ${token}` };
};

export const taskAPI = {
  // Get all tasks or filter by status
  getTasks: async (statusFilter = null) => {
    try {
      const url = statusFilter 
        ? `${API}/tasks?status_filter=${statusFilter}`
        : `${API}/tasks`;
      const response = await axios.get(url, {
        headers: getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to fetch tasks'
      };
    }
  },

  // Get a single task
  getTask: async (taskId) => {
    try {
      const response = await axios.get(`${API}/tasks/${taskId}`, {
        headers: getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to fetch task'
      };
    }
  },

  // Create a new task
  createTask: async (taskData) => {
    try {
      const response = await axios.post(`${API}/tasks`, taskData, {
        headers: getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to create task'
      };
    }
  },

  // Update a task
  updateTask: async (taskId, updateData) => {
    try {
      const response = await axios.put(`${API}/tasks/${taskId}`, updateData, {
        headers: getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to update task'
      };
    }
  },

  // Delete a task
  deleteTask: async (taskId) => {
    try {
      const response = await axios.delete(`${API}/tasks/${taskId}`, {
        headers: getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to delete task'
      };
    }
  }
};
