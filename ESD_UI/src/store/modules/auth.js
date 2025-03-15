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
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      try {
        // Mock successful registration
        const mockUser = { email: userData.email, id: 'mock-user-id' };
        commit('SET_USER', mockUser);
        return mockUser;
      } catch (error) {
        commit('SET_ERROR', 'Registration failed');
        throw new Error('Registration failed');
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async login({ commit }, userData) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      try {
        // Mock successful login
        const mockUser = { email: userData.email, id: 'mock-user-id' };
        commit('SET_USER', mockUser);
        return mockUser;
      } catch (error) {
        commit('SET_ERROR', 'Login failed');
        throw new Error('Login failed');
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async logout({ commit }) {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Mock successful logout
      commit('SET_USER', null);
    },
    
    checkAuthState({ commit }) {
      // Check if there's a user in localStorage
      const savedUser = localStorage.getItem('user');
      if (savedUser) {
        commit('SET_USER', JSON.parse(savedUser));
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