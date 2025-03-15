<template>
  <div class="journey-results">
    <h2>Journey Options</h2>
    <div class="row">
      <div class="col-md-4" v-for="(journey, index) in journeys" :key="index">
        <JourneyCard 
          :transport-mode="journey.transportMode" 
          :travel-time="journey.travelTime" 
          :cost="journey.cost" 
          @save-journey="saveJourney(journey)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import JourneyCard from './JourneyCard.vue';

export default {
  components: {
    JourneyCard,
  },
  props: {
    journeys: {
      type: Array,
      required: true,
    },
  },
  methods: {
    saveJourney(journey) {
      // Logic to save the journey
      this.$emit('save-journey', journey);
    },
  },
};
</script>

<style scoped>
.journey-results {
  margin-top: 20px;
}
</style>