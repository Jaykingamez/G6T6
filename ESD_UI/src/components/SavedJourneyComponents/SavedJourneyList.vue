<template>
  <div class="container mt-4">
    <h2>Saved Journeys</h2>
    <div class="row">
      <div class="col-md-4" v-for="journey in savedJourneys" :key="journey.id">
        <SavedJourneyItem 
          :journey="journey" 
          @edit="editJourney(journey)" 
          @delete="deleteJourney(journey.id)" 
        />
      </div>
    </div>
  </div>
</template>

<script>
import SavedJourneyItem from './SavedJourneyItem.vue';
import { mapState } from 'vuex';

export default {
  components: {
    SavedJourneyItem,
  },
  computed: {
    ...mapState({
      savedJourneys: state => state.journeys.savedJourneys,
    }),
  },
  methods: {
    editJourney(journey) {
      // Logic to edit the journey
      this.$router.push({ name: 'JourneyPlanner', params: { journey } });
    },
    deleteJourney(journeyId) {
      // Logic to delete the journey
      this.$store.dispatch('journeys/deleteJourney', journeyId);
    },
  },
};
</script>

<style scoped>
.container {
  margin-top: 20px;
}
</style>