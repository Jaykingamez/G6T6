<template>
  <div class="journey-planner">
    <div class="planner-header">
      <div class="header-background"></div>
      <div class="header-wrapper">
        <div class="header-content">
          <div class="header-left">
            <div class="header-title">
              <h1>Journey Planner</h1>
              <p class="subtitle">Find the best route for your travel</p>
            </div>
            <div class="stats-container">
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="bi bi-map"></i>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ journeyResults.length }}</span>
                  <span class="stat-label">Available Routes</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="bi bi-clock"></i>
                </div>
                <div class="stat-info">
                  <span class="stat-value">Real-time</span>
                  <span class="stat-label">Updates</span>
                </div>
              </div>
            </div>
          </div>
          <div class="header-right">
            <router-link to="/saved-journeys" class="saved-routes-btn">
              <i class="bi bi-bookmark-check"></i>
              <span>Saved Routes</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="journey-content">
        <div class="journey-form-card">
          <JourneyForm @plan-journey="handleJourneyPlan" />
        </div>
        
        <!-- Loading Indicator -->
        <div v-if="loading" class="loading-state">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading routes...</span>
          </div>
          <p>Getting your journey options...</p>
        </div>
        
        <!-- Error Display -->
        <div v-if="error" class="alert custom-alert">
          <div class="alert-content">
            <i class="bi bi-exclamation-circle"></i>
            <div class="alert-text">
              <h4>Unable to find routes</h4>
              <p>{{ error }}</p>
            </div>
          </div>
          <button class="btn btn-light" @click="retrySearch">
            <i class="bi bi-arrow-clockwise"></i> Try Again
          </button>
        </div>
        
        <!-- Results -->
        <div v-if="journeyResults.length > 0" class="journey-results fade-in">
          <h2>Available Routes</h2>
          <div class="row g-4">
            <div v-for="(journey, index) in journeyResults" :key="index" class="col-md-4">
              <JourneyCard 
                :transport-mode="journey.transportMode" 
                :travel-time="journey.travelTime" 
                :cost="journey.cost"
                :emission="journey.emission"
                :distance="journey.distance"
                :departure-time="journey.departureTime"
                :arrival-time="journey.arrivalTime"
                :steps="journey.steps"
                :route-index="journey.routeIndex"
                :start-point="journey.startPoint"
                :end-point="journey.endPoint"
                @save-journey="saveJourney"
                @view-on-map="viewOnMap"
                @notification-enabled="handleNotificationEnabled"
              />
            </div>
          </div>
        </div>
        
        <div v-if="showMap" class="map-section fade-in">
          <h2>Route Details</h2>
          <div class="map-container">
            <SimplifiedRouteView 
              v-if="selectedJourney" 
              :journey="selectedJourney" 
            />
            <div v-else class="map-placeholder">
              <i class="bi bi-map"></i>
              <p>Select a journey to view route details</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import JourneyForm from '../components/JourneyComponents/JourneyForm.vue';
import JourneyCard from '../components/JourneyComponents/JourneyCard.vue';
import SimplifiedRouteView from '../components/MapComponents/SimplifiedRouteView.vue';

export default {
  components: {
    JourneyForm,
    JourneyCard,
    SimplifiedRouteView,
  },
  data() {
    return {
      journeyResults: [],
      showMap: false,
      selectedJourney: null,
      loading: false,
      error: null,
      rawJourneyResponse: null,
      notificationSuccess: null,
      activeNotifications: [] // Track active notifications
    };
  },
  computed: {
    hasGoogleMapsApiKey() {
      return !!process.env.VUE_APP_GOOGLE_MAPS_API_KEY;
    }
  },
  methods: {
    async handleJourneyPlan(data) {
      this.loading = true;
      this.error = null;
      this.journeyResults = [];
      this.showMap = false;
      this.notificationSuccess = null;
      
      try {
        console.log('Got journey planning data:', data);
        this.rawJourneyResponse = data.journeyResponse;
        
        if (this.rawJourneyResponse && this.rawJourneyResponse.error) {
          // Handle API-returned errors
          throw new Error(this.rawJourneyResponse.error);
        }
        
        // Process the actual API response
        this.processJourneyResponse(data);
      } catch (error) {
        console.error('Error handling journey plan:', error);
        this.error = error.message || 'An error occurred while planning your journey';
      } finally {
        this.loading = false;
      }
    },
    
    processJourneyResponse(data) {
      // Store the raw data in localStorage for debugging
      localStorage.setItem('lastJourneyResponse', JSON.stringify(this.rawJourneyResponse));
      
      // Check if we have a valid response with directions data
      if (!this.rawJourneyResponse || !this.rawJourneyResponse.directions || !this.rawJourneyResponse.directions.routes) {
        this.error = "No route information found in the response";
        return;
      }
      
      const routes = this.rawJourneyResponse.directions.routes;
      const fareCosts = this.rawJourneyResponse.fareCosts || {};
      const emissions = this.rawJourneyResponse.emissions || {};
      const busTracking = this.rawJourneyResponse.busTracking || {};
      
      console.log('Processing fare costs:', fareCosts);
      
      // Transform the Google Directions API response into our card format
      this.journeyResults = routes.map((route, index) => {
        // Get the first leg of the route
        const leg = route.legs[0];
        
        // Calculate total duration in minutes (convert from seconds)
        const durationMinutes = Math.round(leg.duration.value / 60);
        
        // Determine transport mode (looking at the first transit step if available)
        let transportMode = 'Mixed';
        const steps = leg.steps || [];
        
        // Try to find the primary transit mode (bus, subway, etc.)
        for (const step of steps) {
          if (step.travel_mode === 'TRANSIT') {
            if (step.transit_details && step.transit_details.line && step.transit_details.line.vehicle) {
              transportMode = step.transit_details.line.vehicle.name || 'Transit';
              break;
            }
          }
        }
        
        // Check if this is a walking-only route
        if (steps.every(step => step.travel_mode === 'WALKING')) {
          transportMode = 'Walking';
        }
        
        // Get fare cost for this route if available
        let cost = 0;
        
        // First check the new API structure (fareCosts.all_routes[index].total_fare)
        if (fareCosts.all_routes && Array.isArray(fareCosts.all_routes) && fareCosts.all_routes[index]) {
          const routeFare = fareCosts.all_routes[index].total_fare;
          if (routeFare !== undefined) {
            // Convert cents to dollars
            cost = (parseFloat(routeFare) / 100).toFixed(2);
            console.log(`Route ${index} fare from all_routes:`, routeFare, 'formatted to:', cost);
          }
        } 
        // Fall back to old structure if needed
        else if (fareCosts[`route_${index}`] && fareCosts[`route_${index}`].totalFare) {
          cost = (parseFloat(fareCosts[`route_${index}`].totalFare) / 100).toFixed(2);
          console.log(`Route ${index} fare from route_${index}:`, fareCosts[`route_${index}`].totalFare, 'formatted to:', cost);
        }
        // Use total fare as last resort
        else if (fareCosts.totalFare) {
          cost = (parseFloat(fareCosts.totalFare) / 100).toFixed(2);
          console.log(`Route ${index} using global totalFare:`, fareCosts.totalFare, 'formatted to:', cost);
        }
        
        // Get emissions data
        const emission = emissions.routeEmissions && emissions.routeEmissions[index] ?
          emissions.routeEmissions[index].totalEmissions :
          0;

        // Process bus load information for each transit step
        const transitStepsWithLoad = steps.map(step => {
          if (step.travel_mode === 'TRANSIT' && 
              step.transit_details && 
              step.transit_details.line && 
              step.transit_details.line.vehicle && 
              step.transit_details.line.vehicle.name === 'Bus') {
            
            // Try to find matching bus data in busTracking
            const busInfo = this.findBusLoadInfo(busTracking, step);
            if (busInfo) {
              return {
                ...step,
                bus_load: busInfo.load,
                bus_load_description: this.translateBusLoad(busInfo.load),
                next_arrival: busInfo.estimatedArrival,
                bus_stop_code: busInfo.busStopCode // Add bus stop code to the step
              };
            }
          }
          return step;
        });
        
        // Create the journey result object
        return {
          routeIndex: index,
          transportMode: this.formatTransportMode(transportMode),
          travelTime: durationMinutes,
          cost: cost,
          emission: parseFloat(emission).toFixed(2),
          startPoint: data.startPoint,
          endPoint: data.endPoint,
          departureTime: leg.departure_time ? leg.departure_time.text : '',
          arrivalTime: leg.arrival_time ? leg.arrival_time.text : '',
          distance: leg.distance ? leg.distance.text : '',
          steps: transitStepsWithLoad,
          summary: route.summary || '',
          routeData: route, // Store the raw route data for later use
          fareCosts: fareCosts, // Store the fare costs for later use
          busTracking: busTracking // Store the bus tracking data for later use
        };
      });
    },

    // helper method to find bus load info from the busTracking data
    findBusLoadInfo(busTracking, step) {
      if (!busTracking.results || !Array.isArray(busTracking.results)) {
        return null;
      }
      
      // Extract bus service number and bus stop name
      const busNumber = step.transit_details.line.short_name || step.transit_details.line.name;
      const stopName = step.transit_details.departure_stop.name;
      
      // Look for matching bus service in the tracking data
      for (const result of busTracking.results) {
        if (result.arrival_data && result.arrival_data.Services) {
          for (const service of result.arrival_data.Services) {
            // Check if this is the right bus service
            if (service.ServiceNo === busNumber) {
              // Return data from NextBus and include bus stop code
              if (service.NextBus) {
                return {
                  load: service.NextBus.Load,
                  estimatedArrival: service.NextBus.EstimatedArrival,
                  busStopCode: result.arrival_data.BusStopCode // Include the bus stop code
                };
              }
            }
          }
        }
      }
      
      return null;
    },

    // helper method to translate bus load codes to user-friendly descriptions
    translateBusLoad(loadCode) {
      const loadMap = {
        'SEA': 'Seats Available',
        'SDA': 'Standing Available',
        'LSD': 'Limited Standing'
      };
      
      return loadMap[loadCode] || 'Unknown';
    },
    
    formatTransportMode(mode) {
      const modeMap = {
        'BUS': 'Bus',
        'HEAVY_RAIL': 'MRT',
        'SUBWAY': 'MRT',
        'COMMUTER_TRAIN': 'MRT',
        'RAIL': 'MRT',
        'WALKING': 'Walking',
        'Mixed': 'Mixed',
        'Transit': 'Transit'
      };
      
      return modeMap[mode.toUpperCase()] || mode;
    },
    
    saveJourney(journeyData) {
      // Get the full journey data using the routeIndex
      const fullJourney = this.journeyResults[journeyData.routeIndex];
      
      if (!fullJourney) {
        alert('Error: Could not find journey details to save.');
        return;
      }
      
      const journeyToSave = {
        ...journeyData,
        id: Date.now().toString(),
        savedAt: new Date().toISOString(),
        startPoint: fullJourney.startPoint,
        endPoint: fullJourney.endPoint,
        // Additional useful data to save
        distance: fullJourney.distance,
        departure: fullJourney.departureTime,
        arrival: fullJourney.arrivalTime,
        emission: fullJourney.emission,
        // Generate a simple route name
        routeName: `${fullJourney.transportMode} from ${fullJourney.startPoint} to ${fullJourney.endPoint}`
      };
      
      this.$store.dispatch('journeys/saveJourney', journeyToSave);
      alert('Journey saved successfully!');
    },
    
    viewOnMap(journey) {
      // Update the selected journey with all necessary data
      this.selectedJourney = {
        ...journey,
        startPoint: this.journeyResults[journey.routeIndex]?.startPoint || '',
        endPoint: this.journeyResults[journey.routeIndex]?.endPoint || '',
        routeData: this.journeyResults[journey.routeIndex]?.routeData || null,
        steps: this.journeyResults[journey.routeIndex]?.steps || [],
        // Pass the complete fareCosts structure to SimplifiedRouteView
        fareCosts: this.rawJourneyResponse.fareCosts || {}
      };
      
      this.showMap = true;
      
      // Scroll to map section
      setTimeout(() => {
        const mapSection = document.querySelector('.map-section');
        if (mapSection) {
          mapSection.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    },
    
    // New method to handle notification-enabled event from JourneyCard
    handleNotificationEnabled(notificationData) {
      console.log('Notification enabled:', notificationData);
      
      // Add to active notifications
      this.activeNotifications.push(notificationData);
      
      // Show success message
      const busID = notificationData.busID;
      this.notificationSuccess = `You will receive notifications for Bus ${busID} arrivals!`;
      
      // Auto-dismiss after 5 seconds
      setTimeout(() => {
        if (this.notificationSuccess && this.notificationSuccess.includes(`Bus ${busID}`)) {
          this.notificationSuccess = null;
        }
      }, 5000);
    }
  },
};
</script>

<style scoped>
.journey-planner {
  min-height: 100vh;
  background-color: #f8fafc;
  width: 100%;
  margin: 0;
  padding: 0;
  position: relative;
}

.planner-header {
  position: relative;
  background: #1a365d;
  color: white;
  padding: 3rem 0;
  margin: 0;
  width: 100%;
  overflow: hidden;
}

.header-wrapper {
  width: 100%;
  padding: 0 2rem;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  z-index: 1;
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
  opacity: 0.8;
}

.header-background::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.header-left {
  flex: 1;
}

.header-title {
  margin-bottom: 2rem;
}

.header-title h1 {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(to right, #ffffff, #e2e8f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.subtitle {
  font-size: 1.1rem;
  color: #e2e8f0;
  margin: 0.5rem 0 0;
  font-weight: 400;
}

.stats-container {
  display: flex;
  gap: 1.5rem;
  margin-top: 1rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon i {
  font-size: 1.5rem;
  color: #ffffff;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #e2e8f0;
  margin-top: 0.25rem;
}

.header-right {
  display: flex;
  align-items: flex-start;
}

.saved-routes-btn {
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 1rem 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
}

.saved-routes-btn:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 6px 8px rgba(59, 130, 246, 0.3);
  color: white;
}

.content-wrapper {
  width: 100%;
  padding: 2rem;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}

.journey-content {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.journey-form-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 3rem;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.loading-state {
  text-align: center;
  padding: 3rem 0;
}

.loading-state p {
  margin-top: 1rem;
  color: #64748b;
}

.custom-alert {
  background: white;
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.alert-content i {
  font-size: 1.5rem;
  color: #ef4444;
}

.alert-text h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.alert-text p {
  margin: 0.25rem 0 0;
  color: #64748b;
}

.journey-results {
  margin-top: 2rem;
}

.journey-results h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a365d;
  margin-bottom: 1.5rem;
}

.map-section {
  margin-top: 4rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(226, 232, 240, 0.8);
}

.map-section h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a365d;
  margin-bottom: 1.5rem;
}

.map-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  height: 500px;
  overflow: hidden;
}

.map-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #a0aec0;
  background: #f7fafc;
}

.map-placeholder i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* Animations */
.fade-in {
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 991.98px) {
  .header-wrapper {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .header-right {
    width: 100%;
  }
  
  .saved-routes-btn {
    width: 100%;
    justify-content: center;
  }
  
  .journey-form-card {
    padding: 1.5rem;
  }
  
  .content-wrapper {
    padding: 1rem;
  }
}
</style>