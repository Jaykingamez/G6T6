<template>
  <div class="container">
    <h1 class="mt-4 mb-4 text-center">Journey Planner</h1>
    <div class="row">
      <div class="col-lg-8 mx-auto">
        <div class="card shadow-sm">
          <div class="card-body">
            <JourneyForm @plan-journey="fetchJourneyResults" />
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="journeyResults.length > 0" class="mt-5">
      <h2 class="text-center mb-4">Journey Options</h2>
      <div class="row">
        <div v-for="(journey, index) in journeyResults" :key="index" class="col-md-4 mb-4">
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
    
    <div v-if="showMap" class="mt-5">
      <h2 class="text-center mb-4">Journey Map</h2>
      <div class="map-container">
        <!-- Placeholder for map implementation -->
        <div class="alert alert-info text-center">
          Map view will be implemented here using Google Maps or similar service
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
      // This would typically be an API call
      // For now, we'll mock some data
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
      // Add ID and timestamp to journey before saving
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
      // Scroll to map
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
.container {
  max-width: 1200px;
  margin: auto;
  padding-bottom: 50px;
}

.map-container {
  height: 400px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>