<template>
  <div class="journey-planner">
    <div class="planner-header">
      <div class="container">
        <h1 class="text-center mb-2">Plan Your Journey</h1>
        <p class="text-center text-muted">Find the best route for your travel across Singapore</p>
      </div>
    </div>

    <div class="planner-content">
      <div class="container">
        <div class="row">
          <div class="col-lg-10 mx-auto">
            <div class="journey-form-card">
              <JourneyForm @plan-journey="fetchJourneyResults" />
            </div>
          </div>
        </div>
        
        <div v-if="journeyResults.length > 0" class="journey-results fade-in">
          <h2 class="text-center mb-4">Available Routes</h2>
          <div class="row g-4">
            <div v-for="(journey, index) in journeyResults" :key="index" class="col-md-4">
              <JourneyCard 
                :transport-mode="journey.transportMode" 
                :travel-time="journey.travelTime" 
                :cost="journey.cost"
                @save-journey="saveJourney"
                @view-on-map="viewOnMap"
              />
            </div>
          </div>
        </div>
        
        <div v-if="showMap" class="map-section fade-in">
          <h2 class="text-center mb-4">Route Map</h2>
          <div class="map-container">
            <div class="map-placeholder">
              <i class="bi bi-map"></i>
              <p>Interactive map coming soon</p>
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

export default {
  components: {
    JourneyForm,
    JourneyCard,
  },
  data() {
    return {
      journeyResults: [],
      showMap: false,
      selectedJourney: null,
    };
  },
  methods: {
    fetchJourneyResults(query) {
      // Mock data for demonstration
      this.journeyResults = [
        { 
          transportMode: 'MRT', 
          travelTime: 25, 
          cost: 1.60,
          startPoint: query.startPoint,
          endPoint: query.endPoint 
        },
        { 
          transportMode: 'Bus', 
          travelTime: 40, 
          cost: 1.40,
          startPoint: query.startPoint,
          endPoint: query.endPoint 
        },
        { 
          transportMode: 'Taxi', 
          travelTime: 15, 
          cost: 12.80,
          startPoint: query.startPoint,
          endPoint: query.endPoint 
        },
      ];
    },
    saveJourney(journey) {
      const journeyToSave = {
        ...journey,
        id: Date.now().toString(),
        savedAt: new Date().toISOString(),
      };
      
      this.$store.dispatch('journeys/saveJourney', journeyToSave);
      alert('Journey saved successfully!');
    },
    viewOnMap(journey) {
      this.selectedJourney = journey;
      this.showMap = true;
      setTimeout(() => {
        window.scrollTo({
          top: document.body.scrollHeight,
          behavior: 'smooth'
        });
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
  height: 400px;
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