import axios from 'axios';

// Get the API URL from environment variables or use a default
const API_URL = process.env.VUE_APP_USER_API_URL || 'http://localhost:5201';

export default {
  namespaced: true,
  state: {
    user: null,
    loading: false,
    error: null,
  },
  mutations: {
    SET_USER(state, user) {
      state.user = user;
      // Persist user data to localStorage when set
      if (user) {
        localStorage.setItem('user', JSON.stringify(user));
      } else {
        localStorage.removeItem('user');
      }
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
    CLEAR_ERROR(state) {
      state.error = null;
    },
  },
  actions: {
    async register({ commit }, userData) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      try {
        // Call user microservice to create new user
        const response = await axios.post(`${API_URL}/users`, {
          FullName: userData.fullName,
          Email: userData.email,
          Password: userData.password,
          Phone: userData.phone || null // Send null if phone is empty
        });

        if (response.data.code === 201) {
          return response.data.data;
        } else {
          throw new Error(response.data.message || 'Registration failed');
        }
      } catch (error) {
        const errorMessage = error.response?.data?.message || 'Registration failed';
        commit('SET_ERROR', errorMessage);
        throw new Error(errorMessage);
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async login({ commit }, userData) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      try {
        // Use the authenticate endpoint
        const response = await axios.post(`${API_URL}/authenticate`, {
          FullName: userData.fullName,
          Password: userData.password
        });
        
        if (response.data.code === 200) {
          commit('SET_USER', response.data.data);
          return response.data.data;
        } else {
          throw new Error(response.data.message || 'Login failed');
        }
      } catch (error) {
        const errorMessage = error.response?.data?.message || error.message || 'Login failed';
        commit('SET_ERROR', errorMessage);
        throw new Error(errorMessage);
      } finally {
        commit('SET_LOADING', false);
      }
    },

    logout({ commit }) {
      // Clear user from state
      commit('SET_USER', null);
      
      // Ensure localStorage is cleared
      localStorage.removeItem('user');
    },

    // Initialize auth state from localStorage
    initAuth({ commit, dispatch }) {
      const user = localStorage.getItem('user');
      if (user) {
        try {
          commit('SET_USER', JSON.parse(user));
          // After initializing from local storage, verify user still exists on server
          dispatch('checkAuthState');
        } catch (error) {
          console.error('Error parsing user data from localStorage:', error);
          localStorage.removeItem('user');
        }
      }
    },

    // Check if the stored user still exists in the database
    async checkAuthState({ commit, state }) {
      if (!state.user) return;
      
      try {
        const response = await axios.get(`${API_URL}/users/${state.user.UserId}`);
        if (response.data.code !== 200) {
          commit('SET_USER', null);
        }
      } catch (error) {
        commit('SET_USER', null);
      }
    }
  },
  getters: {
    isAuthenticated(state) {
      return !!state.user;
    },
    user(state) {
      return state.user;
    },
    loading(state) {
      return state.loading;
    },
    error(state) {
      return state.error;
    },
  },
};