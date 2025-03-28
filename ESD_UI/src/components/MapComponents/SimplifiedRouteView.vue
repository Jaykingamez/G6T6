<template>
  <div class="simplified-route-view">
    <div class="route-header">
      <h4>{{ journey.transportMode }} Route</h4>
      <div class="route-stats">
        <div class="stat-item">
          <i class="bi bi-clock"></i>
          <span>{{ journey.travelTime }} mins</span>
        </div>
        <div class="stat-item">
          <i class="bi bi-cash"></i>
          <span>${{ formattedCost }}</span>
        </div>
        <div class="stat-item" v-if="journey.distance">
          <i class="bi bi-signpost"></i>
          <span>{{ journey.distance }}</span>
        </div>
        <div class="stat-item" v-if="journey.emission">
          <i class="bi bi-tree"></i>
          <span>{{ journey.emission }} kg CO₂</span>
        </div>
      </div>
    </div>
    
    <div class="route-timeline">
      <div class="start-point">
        <div class="point"></div>
        <div class="point-content">
          <div class="label">{{ journey.startPoint }}</div>
          <div class="time" v-if="journey.departureTime">
            <i class="bi bi-clock me-1"></i>{{ journey.departureTime }}
          </div>
        </div>
      </div>
      
      <div class="steps">
        <div v-for="(step, index) in formattedSteps" :key="index" class="step">
          <div class="step-icon" :class="getStepIconClass(step)">
            <i :class="getStepIcon(step)"></i>
          </div>
          <div class="step-content">
            <div class="step-details">{{ step }}</div>
            <div class="step-line" v-if="index < formattedSteps.length - 1"></div>
          </div>
        </div>
      </div>
      
      <div class="end-point">
        <div class="point"></div>
        <div class="point-content">
          <div class="label">{{ journey.endPoint }}</div>
          <div class="time" v-if="journey.arrivalTime">
            <i class="bi bi-clock me-1"></i>{{ journey.arrivalTime }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    journey: {
      type: Object,
      required: true
    }
  },
  computed: {
    formattedSteps() {
      if (!this.journey.steps || !this.journey.steps.length) {
        return ['Direct route - No detailed steps available'];
      }
      
      return this.formatSteps(this.journey.steps);
    },
    formattedCost() {
      try {
        // Add debugging to check the structure
        console.log('Journey object:', this.journey);
        
        // Check if journey has fareCosts with all_routes
        if (this.journey.fareCosts && 
            this.journey.fareCosts.all_routes && 
            Array.isArray(this.journey.fareCosts.all_routes)) {
            
          console.log('Found fareCosts.all_routes:', this.journey.fareCosts.all_routes);
          
          // Get route index (default to 0 if not provided)
          const routeIndex = this.journey.routeIndex !== undefined ? 
            this.journey.routeIndex : 0;
          
          console.log('Using route index:', routeIndex);
            
          // Check if the route exists at that index
          if (this.journey.fareCosts.all_routes[routeIndex]) {
            const totalFare = this.journey.fareCosts.all_routes[routeIndex].total_fare;
            console.log('Found total_fare:', totalFare);
            
            // Convert cents to dollars (divide by 100)
            return (parseFloat(totalFare) / 100).toFixed(2);
          }
        }
        
        // Check if journey response has fareCosts
        if (this.journey.journeyResponse && 
            this.journey.journeyResponse.fareCosts && 
            this.journey.journeyResponse.fareCosts.all_routes) {
            
          console.log('Found in journeyResponse:', this.journey.journeyResponse.fareCosts.all_routes);
          
          const routeIndex = this.journey.routeIndex !== undefined ? 
            this.journey.routeIndex : 0;
            
          if (this.journey.journeyResponse.fareCosts.all_routes[routeIndex]) {
            const totalFare = this.journey.journeyResponse.fareCosts.all_routes[routeIndex].total_fare;
            console.log('Found total_fare in journeyResponse:', totalFare);
            
            return (parseFloat(totalFare) / 100).toFixed(2);
          }
        }
        
        // Fallback to direct cost property if available
        if (this.journey.cost !== undefined) {
          console.log('Using direct cost:', this.journey.cost);
          return (parseFloat(this.journey.cost) / 100).toFixed(2);
        }
        
        // Default fallback
        console.log('No fare data found, using default 0.00');
        return '0.00';
      } catch (error) {
        console.error('Error calculating fare:', error);
        return '0.00';
      }
    }
  },
  methods: {
    formatSteps(steps) {
      const formattedSteps = [];
      
      for (const step of steps) {
        if (step.travel_mode === 'TRANSIT') {
          const transit = step.transit_details;
          if (transit) {
            const vehicleType = transit.line?.vehicle?.name || 'Transit';
            // Rename "Subway" to "MRT" for Singapore context
            const localizedVehicleType = vehicleType === 'Subway' ? 'MRT' : vehicleType;
            const routeName = transit.line?.short_name || transit.line?.name || '';
            const stops = transit.num_stops || 0;
            const duration = step.duration ? ` (${Math.round(step.duration.value / 60)} mins)` : '';
            formattedSteps.push(`${localizedVehicleType} ${routeName} - ${stops} stops${duration}`);
          }
        } else if (step.travel_mode === 'WALKING') {
          if (step.distance && step.distance.value > 100) {
            const duration = step.duration ? ` (${Math.round(step.duration.value / 60)} mins)` : '';
            formattedSteps.push(`Walk ${step.distance.text}${duration}`);
          }
        }
      }
      
      return formattedSteps.length ? formattedSteps : ['Direct route'];
    },
    getStepIcon(step) {
      if (step.includes('Bus')) return 'bi bi-bus-front';
      if (step.includes('MRT') || step.includes('Subway') || step.includes('train')) return 'bi bi-train-front';
      if (step.includes('Walk')) return 'bi bi-person-walking';
      if (step.includes('Direct route')) return 'bi bi-arrow-right';
      return 'bi bi-arrow-right';
    },
    getStepIconClass(step) {
      if (step.includes('Bus')) return 'bus-icon';
      if (step.includes('MRT') || step.includes('Subway') || step.includes('train')) return 'mrt-icon';
      if (step.includes('Walk')) return 'walk-icon';
      return 'default-icon';
    }
  }
};
</script>

<style scoped>
.simplified-route-view {
  background: white;
  border-radius: 16px;
  padding: 24px;
  height: 100%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.route-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.route-header h4 {
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0;
}

.route-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f7fafc;
  padding: 8px 12px;
  border-radius: 8px;
}

.stat-item i {
  color: #4299e1;
  font-size: 1.1rem;
}

.route-timeline {
  position: relative;
  padding-left: 40px;
}

.route-timeline::before {
  content: '';
  position: absolute;
  top: 24px;
  bottom: 24px;
  left: 12px;
  width: 3px;
  background: #e2e8f0;
}

.start-point, .end-point {
  position: relative;
  padding: 16px 0;
  display: flex;
  align-items: flex-start;
}

.point {
  position: absolute;
  left: -40px;
  top: 20px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  z-index: 1;
}

.start-point .point {
  background: #4299e1;
}

.end-point .point {
  background: #48bb78;
}

.point-content {
  flex: 1;
}

.label {
  font-weight: 700;
  margin-bottom: 4px;
  color: #2d3748;
}

.time {
  color: #718096;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
}

.steps {
  margin: 8px 0;
}

.step {
  display: flex;
  margin-bottom: 8px;
  position: relative;
}

.step-icon {
  position: absolute;
  left: -40px;
  top: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  color: white;
  z-index: 1;
}

.step-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.step-details {
  padding: 12px 16px;
  background: #f7fafc;
  border-radius: 8px;
  font-size: 0.95rem;
  margin-bottom: 8px;
  color: #4a5568;
}

.step-line {
  height: 12px;
}

/* Icon styles */
.bus-icon {
  background: #3182ce;
}

.mrt-icon {
  background: #38a169;
}

.walk-icon {
  background: #718096;
}

.default-icon {
  background: #a0aec0;
}

@media (max-width: 768px) {
  .route-stats {
    flex-direction: column;
    gap: 8px;
  }
  
  .simplified-route-view {
    padding: 16px;
  }
  
  .route-timeline {
    padding-left: 32px;
  }
  
  .point, .step-icon {
    left: -32px;
    width: 20px;
    height: 20px;
  }
}
</style>