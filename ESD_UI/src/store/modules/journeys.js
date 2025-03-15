export default {
  namespaced: true,
  state: {
    savedJourneys: [],
    loading: false,
    error: null,
  },
  mutations: {
    SET_SAVED_JOURNEYS(state, journeys) {
      state.savedJourneys = journeys;
    },
    ADD_JOURNEY(state, journey) {
      state.savedJourneys.push(journey);
    },
    REMOVE_JOURNEY(state, journeyId) {
      state.savedJourneys = state.savedJourneys.filter(j => j.id !== journeyId);
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
  },
  actions: {
    async fetchSavedJourneys({ commit }) {
      commit('SET_LOADING', true);
      
      try {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Mock data
        const mockJourneys = [
          {
            id: '1',
            startPoint: 'Changi Airport',
            endPoint: 'Marina Bay Sands',
            transportMode: 'MRT',
            travelTime: 35,
            cost: 2.50,
            savedAt: '2023-03-01T08:30:00Z'
          },
          {
            id: '2',
            startPoint: 'Orchard Road',
            endPoint: 'Sentosa',
            transportMode: 'Bus',
            travelTime: 45,
            cost: 1.80,
            savedAt: '2023-02-15T14:20:00Z'
          },
          {
            id: '3',
            startPoint: 'Jurong East',
            endPoint: 'Changi Business Park',
            transportMode: 'Taxi',
            travelTime: 30,
            cost: 22.50,
            savedAt: '2023-02-28T18:45:00Z'
          }
        ];
        
        commit('SET_SAVED_JOURNEYS', mockJourneys);
      } catch (error) {
        commit('SET_ERROR', 'Failed to fetch saved journeys');
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async saveJourney({ commit }, journeyData) {
      commit('SET_LOADING', true);
      
      try {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Generate fake ID and timestamp
        const newJourney = {
          ...journeyData,
          id: Date.now().toString(),
          savedAt: new Date().toISOString()
        };
        
        commit('ADD_JOURNEY', newJourney);
      } catch (error) {
        commit('SET_ERROR', 'Failed to save journey');
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async removeJourney({ commit }, journeyId) {
      commit('SET_LOADING', true);
      
      try {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        commit('REMOVE_JOURNEY', journeyId);
      } catch (error) {
        commit('SET_ERROR', 'Failed to remove journey');
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    }
  },
  getters: {
    allSavedJourneys(state) {
      return state.savedJourneys;
    },
    loading(state) {
      return state.loading;
    },
    error(state) {
      return state.error;
    }
  }
};