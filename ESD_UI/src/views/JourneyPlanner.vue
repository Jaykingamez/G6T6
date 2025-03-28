<template>
  <div class="journey-planner">
    <div class="planner-header">
      <div class="container">
        <h1 class="text-center mb-2">Plan Your Journey</h1>
        <p class="text-center text-white">Find the best route for your travel across Singapore</p>
      </div>
    </div>

    <div class="planner-content">
      <div class="container">
        <div class="row">
          <div class="col-lg-10 mx-auto">
            <div class="journey-form-card">
              <JourneyForm @plan-journey="handleJourneyPlan" />
            </div>
          </div>
        </div>
        
        <!-- Loading Indicator -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading routes...</span>
          </div>
          <p class="mt-2">Getting your journey options...</p>
        </div>
        
        <!-- Error Display -->
        <div v-if="error" class="alert alert-danger mx-auto mt-4" style="max-width: 800px;">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          <strong>Error:</strong> {{ error }}
        </div>
        
        <!-- Results -->
        <div v-if="journeyResults.length > 0" class="journey-results fade-in">
          <h2 class="text-center mb-4">Available Routes</h2>
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
                @save-journey="saveJourney"
                @view-on-map="viewOnMap(journey)"
              />
            </div>
          </div>
        </div>
        
        <div v-if="showMap" class="map-section fade-in">
          <h2 class="text-center mb-4">Route Details</h2>
          <div class="map-container">
            <RouteMap 
              v-if="selectedJourney && hasGoogleMapsApiKey" 
              :journey="selectedJourney" 
            />
            <SimplifiedRouteView 
              v-else-if="selectedJourney" 
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
          steps: steps,
          summary: route.summary || '',
          routeData: route, // Store the raw route data for later use
          fareCosts: fareCosts // Store the fare costs for later use
        };
      });
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
    }
  },
};
</script>

<style scoped>
.journey-planner {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
}

.planner-header {
  background: linear-gradient(135deg, #2c5282 0%, #4299e1 100%);
  padding: 4rem 0 8rem;
  margin-bottom: -4rem;
  color: white;
  position: relative;
  overflow: hidden;
}

.planner-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  /* background-image: url('@/assets/pattern.png'); */
  opacity: 0.1;
  pointer-events: none;
}

.planner-header h1 {
  font-size: 2.75rem;
  font-weight: 800;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.planner-content {
  position: relative;
  padding: 0 0 4rem;
}

.journey-form-card {
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 3rem;
  border: 1px solid rgba(226, 232, 240, 0.8);
  backdrop-filter: blur(10px);
}

.journey-results {
  margin-top: 4rem;
}

.journey-results h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 2rem;
}

.map-section {
  margin-top: 4rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(226, 232, 240, 0.8);
}

.map-container {
  background: white;
  border-radius: 24px;
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
  .planner-header {
    padding: 3rem 0 7rem;
  }

  .planner-header h1 {
    font-size: 2.25rem;
  }

  .journey-form-card {
    padding: 1.5rem;
  }
}
</style>