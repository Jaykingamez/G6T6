<template>
  <div class="journey-card">
    <div class="card h-100 shadow-sm">
      <div :class="['card-header', getTransportClass(transportMode)]">
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="mb-0">{{ transportMode }}</h5>
          <span class="transport-icon">
            <i :class="getTransportIcon(transportMode)"></i>
          </span>
        </div>
      </div>
      <div class="card-body">
        <div class="journey-details">
          <div class="journey-time mb-3">
            <div class="d-flex justify-content-between">
              <div>
                <strong>Travel Time:</strong> {{ travelTime }} mins
              </div>
              <div v-if="departureTime && arrivalTime">
                <small class="text-muted">{{ departureTime }} - {{ arrivalTime }}</small>
              </div>
            </div>
            <div v-if="distance" class="mt-1">
              <small class="text-muted">Distance: {{ distance }}</small>
            </div>
          </div>
          
          <div class="journey-cost mb-3">
            <strong>Cost:</strong> ${{ parseFloat(cost).toFixed(2) }}
          </div>
          
          <div v-if="emission" class="journey-emissions mb-3">
            <strong>CO₂ Emission:</strong> {{ emission }} kg
            <div class="emission-indicator mt-1">
              <div class="progress" style="height: 6px;">
                <div 
                  class="progress-bar" 
                  role="progressbar" 
                  :style="{width: getEmissionIndicator(emission) + '%'}" 
                  :class="getEmissionClass(emission)">
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="steps && steps.length" class="journey-steps">
            <strong>Key Steps:</strong>
            <ul class="list-unstyled small mt-2">
              <li v-for="(step, index) in formatSteps(steps)" :key="index" class="mb-1">
                <div class="d-flex align-items-center">
                  <i :class="getStepIcon(step.text)" class="me-1"></i> 
                  <span>{{ step.text }}</span>
                  <span v-if="step.busLoad" :class="getBusLoadClass(step.busLoad)" class="ms-2 px-1 small rounded">
                    {{ step.busLoad }}
                  </span>
                </div>
              </li>
            </ul>
          </div>
          
          <!-- Bus Notification Button - Only show for bus routes -->
          <div v-if="hasBusTransit" class="mt-3">
            <button 
              class="btn btn-sm w-100" 
              :class="notificationEnabled ? 'btn-success' : 'btn-outline-primary'"
              @click="toggleBusNotification"
              :disabled="notificationLoading"
            >
              <i class="bi" :class="notificationIcon"></i>
              {{ notificationButtonText }}
              <span v-if="notificationLoading" class="spinner-border spinner-border-sm ms-1" role="status" aria-hidden="true"></span>
            </button>
            <small v-if="notificationError" class="text-danger d-block mt-1">
              {{ notificationError }}
            </small>
          </div>
        </div>
      </div>
      <div class="card-footer bg-white border-0">
        <div class="d-flex justify-content-between">
          <!-- <button 
            class="btn btn-outline-primary btn-sm" 
            @click="viewOnMap"
            title="View this route on the map">
            <i class="bi bi-map"></i> View Map
          </button>
          <button 
            class="btn btn-outline-success btn-sm" 
            @click="handleSave"
            title="Save this route to your favorites">
            <i class="bi bi-bookmark-plus"></i> Save
          </button> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    transportMode: {
      type: String,
      required: true
    },
    travelTime: {
      type: Number,
      required: true
    },
    cost: {
      type: [Number, String],
      required: true
    },
    emission: {
      type: [Number, String],
      default: 0
    },
    distance: {
      type: String,
      default: ''
    },
    departureTime: {
      type: String,
      default: ''
    },
    arrivalTime: {
      type: String,
      default: ''
    },
    steps: {
      type: Array,
      default: () => []
    },
    routeIndex: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      notificationEnabled: false,
      notificationLoading: false,
      notificationError: null,
      routeID: null
    };
  },
  computed: {
    hasBusTransit() {
      // Check if this journey has any bus transit steps
      if (!this.steps || this.steps.length === 0) return false;
      
      return this.steps.some(step => 
        step.travel_mode === 'TRANSIT' && 
        step.transit_details && 
        step.transit_details.line && 
        step.transit_details.line.vehicle && 
        step.transit_details.line.vehicle.name === 'Bus'
      );
    },
    busTransitDetails() {
      // Get details of the first bus transit step
      if (!this.hasBusTransit) return null;
      
      const busStep = this.steps.find(step => 
        step.travel_mode === 'TRANSIT' && 
        step.transit_details && 
        step.transit_details.line && 
        step.transit_details.line.vehicle && 
        step.transit_details.line.vehicle.name === 'Bus'
      );
      
      if (!busStep) return null;
      
      return {
        busID: busStep.transit_details.line.short_name || busStep.transit_details.line.name,
        busStopCode: this.getBusStopCode(busStep),
        userID: 3 // Hardcoded for now, should be retrieved from user session/store
      };
    },
    notificationButtonText() {
      if (this.notificationEnabled) {
        return 'Bus Notifications Enabled';
      }
      return 'Enable Bus Notifications';
    },
    notificationIcon() {
      if (this.notificationEnabled) {
        return 'bi-bell-fill';
      }
      return 'bi-bell';
    }
  },
  methods: {
    getTransportClass(mode) {
      const modeMap = {
        'Bus': 'bg-primary text-white',
        'MRT': 'bg-success text-white',
        'Walking': 'bg-info text-white',
        'Taxi': 'bg-warning text-dark',
        'Mixed': 'bg-secondary text-white'
      };
      return modeMap[mode] || 'bg-secondary text-white';
    },
    getTransportIcon(mode) {
      const iconMap = {
        'Bus': 'bi bi-bus-front',
        'MRT': 'bi bi-train-front',
        'Walking': 'bi bi-person-walking',
        'Taxi': 'bi bi-taxi-front',
        'Mixed': 'bi bi-arrow-repeat'
      };
      return iconMap[mode] || 'bi bi-signpost-2';
    },
    getStepIcon(step) {
      if (step.includes('Bus')) return 'bi bi-bus-front';
      if (step.includes('MRT') || step.includes('train')) return 'bi bi-train-front';
      if (step.includes('Walk')) return 'bi bi-person-walking';
      return 'bi bi-arrow-right';
    },
    formatSteps(steps) {
      // Extract key information from steps to display a summary
      const formattedSteps = [];
      
      for (const step of steps) {
        if (step.travel_mode === 'TRANSIT') {
          const transit = step.transit_details;
          if (transit) {
            const vehicleType = transit.line?.vehicle?.name || 'Transit';
            const routeName = transit.line?.short_name || transit.line?.name || '';
            const stops = transit.num_stops || 0;
            let stepText = `${vehicleType} ${routeName} (${stops} stops)`;
            
            // Add bus load info if available and it's a bus
            let busLoad = null;
            if (vehicleType === 'Bus' && step.bus_load_description) {
              busLoad = step.bus_load_description;
            }
            
            formattedSteps.push({
              text: stepText,
              busLoad: busLoad
            });
          }
        } else if (step.travel_mode === 'WALKING') {
          // Only include walking steps that are substantial
          if (step.distance && step.distance.value > 100) {
            formattedSteps.push({
              text: `Walk ${step.distance.text}`,
              busLoad: null
            });
          }
        }
      }
      
      // Limit to 3 key steps maximum
      return formattedSteps.slice(0, 3);
    },
    getBusLoadClass(loadDescription) {
      // Style different load levels with different colors
      if (loadDescription === 'Seats Available') return 'bg-success text-white';
      if (loadDescription === 'Standing Available') return 'bg-warning text-dark';
      if (loadDescription === 'Limited Standing') return 'bg-danger text-white';
      return 'bg-secondary text-white';
    },
    getEmissionIndicator(emission) {
      // Scale the emissions to a percentage (0-100) for the progress bar
      // Assuming 5kg is the max that would reach 100%
      const maxEmission = 5;
      return Math.min(parseFloat(emission) / maxEmission * 100, 100);
    },
    getEmissionClass(emission) {
      const value = parseFloat(emission);
      if (value < 1) return 'bg-success';
      if (value < 2) return 'bg-info';
      if (value < 3) return 'bg-warning';
      return 'bg-danger';
    },
    handleSave() {
      this.$emit('save-journey', {
        transportMode: this.transportMode,
        travelTime: this.travelTime,
        cost: this.cost,
        emission: this.emission,
        routeIndex: this.routeIndex
      });
    },
    viewOnMap() {
      this.$emit('view-on-map', {
        transportMode: this.transportMode,
        travelTime: this.travelTime,
        cost: this.cost,
        emission: this.emission,
        routeIndex: this.routeIndex,
        steps: this.steps
      });
    },
    // New methods for bus notification functionality
    getBusStopCode(busStep) {
      // First check if we have the bus stop code from the API response
      if (busStep.bus_stop_code) {
        return busStep.bus_stop_code;
      }
      
      // Check if it's available in transit details
      if (busStep?.transit_details?.departure_stop?.code) {
        return busStep.transit_details.departure_stop.code;
      }
      
      // If no bus stop code is available, look for it in the raw data
      const busNumber = busStep?.transit_details?.line?.short_name || 
                        busStep?.transit_details?.line?.name;
      
      // Try to find it in the steps data - this assumes your busTracking data
      // has been processed and attached to the step somewhere in your journey results
      
      // If all else fails, log a warning and return a default
      console.warn('Could not determine bus stop code for', busNumber);
      return '00000'; // Use a clearly invalid code instead of 1, so it's obvious something is wrong
    },
    async toggleBusNotification() {
      if (this.notificationEnabled) {
        // TODO: Add logic to disable notifications if needed
        this.notificationEnabled = false;
        return;
      }
      
      if (!this.busTransitDetails) {
        this.notificationError = "Could not determine bus details";
        return;
      }
      
      this.notificationLoading = true;
      this.notificationError = null;
      
      try {
        // Step 1: Create SQL entry
        const response = await fetch('http://localhost:5301/selectedroute', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            BusStopCode: this.busTransitDetails.busStopCode,
            BusID: this.busTransitDetails.busID,
            UserID: this.busTransitDetails.userID
          }),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.message || 'Failed to save route');
        }
        
        // Store the RouteID for potential future use
        this.routeID = data.data.RouteID;
        
        // Step 2: Enable notification using the RouteID
        const notificationResponse = await fetch(`http://localhost:5302/enable_notification/${this.routeID}`, {
          method: 'GET'
        });
        
        const notificationData = await notificationResponse.json();
        
        if (!notificationResponse.ok) {
          throw new Error(notificationData.message || 'Failed to enable notifications');
        }
        
        // Success!
        this.notificationEnabled = true;
        
        // Emit an event to inform parent components
        this.$emit('notification-enabled', {
          routeID: this.routeID,
          busID: this.busTransitDetails.busID,
          busStopCode: this.busTransitDetails.busStopCode
        });
        
      } catch (error) {
        console.error('Error setting up notifications:', error);
        this.notificationError = error.message || 'Failed to set up notifications';
        this.notificationEnabled = false;
      } finally {
        this.notificationLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.journey-card {
  height: 100%;
}

.transport-icon {
  font-size: 1.25rem;
}

.emission-indicator {
  height: 6px;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}
</style>