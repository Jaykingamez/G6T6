import { getSavedJourneys, deleteJourney, saveJourney } from '@/services/api';

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
    async fetchSavedJourneys({ commit, rootState }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        // Get the current user ID from auth module
        const userId = rootState.auth.user?.UserId;
        
        console.log('Current user state:', rootState.auth.user);
        console.log('Using user ID for routes:', userId);
        
        if (!userId) {
          throw new Error('User ID not available. Please log in again.');
        }
        
        const response = await getSavedJourneys(userId);
        
        if (response.code === 200) {
          // Extract routes from the selectedRoute service response
          const routes = response.data?.routes || [];
          
          // Transform the data to match our UI format
          const transformedJourneys = routes.map(route => ({
            id: route.RouteID,
            startPoint: route.BusStopCode || 'Unknown start',
            endPoint: route.BusID || 'Unknown destination',
            transportMode: 'Bus', // Default to bus since we're using BusID
            travelTime: 0, // This data might not be available from selectedRoute
            cost: 0,       // This data might not be available from selectedRoute
            savedAt: new Date().toISOString(),
            routeName: `Route from ${route.BusStopCode} via ${route.BusID}`
          }));
          
          commit('SET_SAVED_JOURNEYS', transformedJourneys);
        } else {
          throw new Error(response.message || 'Failed to fetch journeys');
        }
      } catch (error) {
        console.error('Error in fetchSavedJourneys:', error);
        commit('SET_ERROR', error.message || 'Failed to fetch saved journeys');
        
        // Fall back to empty array
        commit('SET_SAVED_JOURNEYS', []);
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async saveJourney({ commit, rootState }, journeyData) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const userId = rootState.auth.user?.UserId;
        
        if (!userId) {
          throw new Error('User ID not available. Please log in again.');
        }
        
        // Format the data for the API
        const routeData = {
          user_id: userId,
          route_name: journeyData.routeName || `Journey to ${journeyData.endPoint}`,
          route_data: journeyData // Include all journey details
        };
        
        const response = await saveJourney(routeData);
        
        if (response.code === 201) {
          const savedJourney = {
            id: response.data.id,
            startPoint: journeyData.startPoint,
            endPoint: journeyData.endPoint,
            transportMode: journeyData.transportMode,
            travelTime: journeyData.travelTime,
            cost: journeyData.cost,
            savedAt: response.data.created_at || new Date().toISOString(),
            routeName: response.data.route_name
          };
          
          commit('ADD_JOURNEY', savedJourney);
          return savedJourney;
        } else {
          throw new Error(response.message || 'Failed to save journey');
        }
      } catch (error) {
        console.error('Error in saveJourney:', error);
        commit('SET_ERROR', error.message || 'Failed to save journey');
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async removeJourney({ commit }, journeyId) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        // Call the selectedRoute service to delete the route
        const response = await axios.delete(`http://localhost:5301/selectedroute/${journeyId}`);
        
        if (response.data.code === 200) {
          commit('REMOVE_JOURNEY', journeyId);
          return true;
        } else {
          throw new Error(response.data.message || 'Failed to remove journey');
        }
      } catch (error) {
        console.error('Error in removeJourney:', error);
        commit('SET_ERROR', error.message || 'Failed to remove journey');
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