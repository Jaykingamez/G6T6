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
                <i :class="getStepIcon(step)"></i> {{ step }}
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div class="card-footer bg-white border-0">
        <div class="d-flex justify-content-between">
          <button 
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
          </button>
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
            formattedSteps.push(`${vehicleType} ${routeName} (${stops} stops)`);
          }
        } else if (step.travel_mode === 'WALKING') {
          // Only include walking steps that are substantial
          if (step.distance && step.distance.value > 100) {
            formattedSteps.push(`Walk ${step.distance.text}`);
          }
        }
      }
      
      // Limit to 3 key steps maximum
      return formattedSteps.slice(0, 3);
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