<template>
  <div class="route-map-container">
    <div v-if="loading" class="map-loading">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading map...</span>
      </div>
    </div>
    
    <div id="map" ref="mapContainer" class="map-element"></div>
    
    <div v-if="routeInfo" class="route-info-panel">
      <div class="route-overview">
        <h6 class="mb-2">{{ routeInfo.transportMode }} Route</h6>
        <div class="d-flex justify-content-between mb-2">
          <span>
            <i class="bi bi-clock me-1"></i> {{ routeInfo.travelTime }} mins
          </span>
          <span>
            <i class="bi bi-cash me-1"></i> ${{ parseFloat(routeInfo.cost).toFixed(2) }}
          </span>
        </div>
        <div v-if="routeInfo.steps.length" class="route-steps">
          <div v-for="(step, index) in formattedSteps" :key="index" class="route-step">
            <div class="step-icon">
              <i :class="getStepIcon(step)"></i>
            </div>
            <div class="step-content">
              {{ step }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RouteMap',
  props: {
    journey: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      map: null,
      directionsService: null,
      directionsRenderer: null,
      formattedSteps: [],
      routeInfo: null
    };
  },
  computed: {
    hasApiKey() {
      return !!process.env.VUE_APP_GOOGLE_MAPS_API_KEY;
    }
  },
  mounted() {
    this.initializeMap();
  },
  methods: {
    initializeMap() {
      this.loading = true;
      
      // Set route info for the panel
      this.routeInfo = {
        transportMode: this.journey.transportMode,
        travelTime: this.journey.travelTime,
        cost: this.journey.cost,
        steps: this.journey.steps || []
      };
      
      // Format steps for display
      this.formatRouteSteps();
      
      // Check if we have the Google Maps API key
      if (!this.hasApiKey) {
        console.warn("No Google Maps API key provided. Using fallback display.");
        this.loading = false;
        return;
      }
      
      // Load Google Maps API
      if (!window.google || !window.google.maps) {
        this.loadGoogleMapsAPI()
          .then(() => this.setupMap())
          .catch(error => {
            console.error('Error loading Google Maps API:', error);
            this.loading = false;
          });
      } else {
        this.setupMap();
      }
    },
    
    loadGoogleMapsAPI() {
      return new Promise((resolve, reject) => {
        // Check if the script is already loading
        if (document.querySelector('script[src*="maps.googleapis.com/maps/api/js"]')) {
          // If script is already in the process of loading, wait for it
          if (window.google && window.google.maps) {
            resolve();
            return;
          }
          
          const waitForGoogleMaps = setInterval(() => {
            if (window.google && window.google.maps) {
              clearInterval(waitForGoogleMaps);
              resolve();
            }
          }, 100);
          return;
        }
        
        try {
          // Create script element
          const script = document.createElement('script');
          script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.VUE_APP_GOOGLE_MAPS_API_KEY}`;
          script.async = true;
          script.defer = true;
          
          // Set up event handlers
          script.onload = () => resolve();
          script.onerror = () => reject(new Error('Failed to load Google Maps API'));
          
          // Add script to document
          document.head.appendChild(script);
        } catch (error) {
          reject(error);
        }
      });
    },
    
    setupMap() {
      try {
        const mapElement = this.$refs.mapContainer;
        
        // Create map
        this.map = new google.maps.Map(mapElement, {
          center: { lat: 1.3521, lng: 103.8198 }, // Singapore
          zoom: 12,
          mapTypeControl: false,
          fullscreenControl: true,
          streetViewControl: false
        });
        
        // Set up directions service and renderer
        this.directionsService = new google.maps.DirectionsService();
        this.directionsRenderer = new google.maps.DirectionsRenderer({
          map: this.map,
          suppressMarkers: false,
          polylineOptions: {
            strokeColor: this.getRouteColor(this.journey.transportMode),
            strokeWeight: 5
          }
        });
        
        // Display the route
        this.displayRoute();
      } catch (error) {
        console.error('Error setting up map:', error);
        this.loading = false;
      }
    },
    
    displayRoute() {
      try {
        // If no start/end point data, show error and return
        if (!this.journey.startPoint || !this.journey.endPoint) {
          console.error('Missing start or end point data');
          this.loading = false;
          return;
        }
        
        // Request directions from Google Maps API
        const request = {
          origin: this.journey.startPoint,
          destination: this.journey.endPoint,
          travelMode: this.getTravelMode(this.journey.transportMode)
        };
        
        this.directionsService.route(request, (result, status) => {
          if (status === 'OK') {
            this.directionsRenderer.setDirections(result);
          } else {
            console.error('Directions request failed due to:', status);
          }
          this.loading = false;
        });
      } catch (error) {
        console.error('Error displaying route:', error);
        this.loading = false;
      }
    },
    
    formatRouteSteps() {
      if (!this.journey.steps || !this.journey.steps.length) {
        this.formattedSteps = [];
        return;
      }
      
      // For each step, create a readable description
      const steps = [];
      
      for (const step of this.journey.steps) {
        if (step.travel_mode === 'TRANSIT') {
          const transit = step.transit_details;
          if (transit) {
            const vehicleType = transit.line?.vehicle?.name || 'Transit';
            const routeName = transit.line?.short_name || transit.line?.name || '';
            const stops = transit.num_stops || 0;
            steps.push(`${vehicleType} ${routeName} (${stops} stops)`);
          }
        } else if (step.travel_mode === 'WALKING') {
          if (step.distance && step.distance.value > 100) {
            steps.push(`Walk ${step.distance.text}`);
          }
        }
      }
      
      this.formattedSteps = steps.length ? steps : ['No step information available'];
    },
    
    getTravelMode(mode) {
      const modeMap = {
        'Bus': 'TRANSIT',
        'MRT': 'TRANSIT',
        'Walking': 'WALKING',
        'Taxi': 'DRIVING',
        'Mixed': 'TRANSIT'
      };
      
      return modeMap[mode] || 'TRANSIT';
    },
    
    getRouteColor(mode) {
      const colorMap = {
        'Bus': '#4285F4', // Blue
        'MRT': '#0F9D58', // Green
        'Walking': '#34A853', // Green
        'Taxi': '#FBBC04', // Yellow
        'Mixed': '#7D3C98'  // Purple
      };
      
      return colorMap[mode] || '#4285F4';
    },
    
    getStepIcon(step) {
      if (step.includes('Bus')) return 'bi bi-bus-front';
      if (step.includes('MRT') || step.includes('train')) return 'bi bi-train-front';
      if (step.includes('Walk')) return 'bi bi-person-walking';
      return 'bi bi-arrow-right';
    }
  }
};
</script>

<style scoped>
.route-map-container {
  position: relative;
  height: 500px;
  width: 100%;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.map-element {
  height: 100%;
  width: 100%;
}

.map-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 10;
}

.route-info-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  background: white;
  border-radius: 8px;
  padding: 16px;
  width: 280px;
  max-height: 400px;
  overflow-y: auto;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  z-index: 5;
}

.route-steps {
  margin-top: 15px;
}

.route-step {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #e2e8f0;
}

.route-step:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.step-icon {
  flex: 0 0 30px;
  text-align: center;
  color: #4299e1;
}

.step-content {
  flex: 1;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .route-info-panel {
    width: calc(100% - 40px);
    max-height: 200px;
  }
}
</style>