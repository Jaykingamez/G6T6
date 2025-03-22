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
          Phone: userData.phone
        });

        if (response.data.code === 201) {
          commit('SET_USER', response.data.data);
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
        // Get all users and find matching user
        const response = await axios.get(`${API_URL}/users`);
        const users = Array.isArray(response.data) ? response.data : [];
        
        // Find user with matching full name and phone
        const user = users.find(u => 
          u.FullName.toLowerCase() === userData.fullName.toLowerCase() && 
          u.Phone === userData.phone
        );
        
        if (user) {
          commit('SET_USER', user);
          return user;
        } else {
          throw new Error('Invalid credentials');
        }
      } catch (error) {
        const errorMessage = error.response?.data?.message || error.message || 'Login failed';
        commit('SET_ERROR', errorMessage);
        throw new Error(errorMessage);
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async logout({ commit }) {
      try {
        commit('SET_USER', null); // This will also remove from localStorage
      } catch (error) {
        console.error('Logout error:', error);
        throw new Error('Logout failed');
      }
    },
    
    checkAuthState({ commit }) {
      try {
        const savedUser = localStorage.getItem('user');
        if (savedUser) {
          const user = JSON.parse(savedUser);
          // Verify user still exists in database
          axios.get(`${API_URL}/users/${user.UserId}`)
            .then(response => {
              if (response.data.code === 200) {
                commit('SET_USER', response.data.data);
              } else {
                // User no longer exists in database
                commit('SET_USER', null);
              }
            })
            .catch(() => {
              // If error occurs, clear the stored user
              commit('SET_USER', null);
            });
        }
      } catch (error) {
        console.error('Error checking auth state:', error);
        // If there's an error reading from localStorage, clear it
        localStorage.removeItem('user');
        commit('SET_USER', null);
      }
    },
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