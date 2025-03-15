<template>
  <div class="saved-journey-item card mb-3">
    <div class="card-body">
      <h5 class="card-title">{{ journey.startPoint }} to {{ journey.endPoint }}</h5>
      <p class="card-text">Transport Mode: {{ journey.transportMode }}</p>
      <p class="card-text">Estimated Travel Time: {{ journey.travelTime }}</p>
      <p class="card-text">Cost: {{ journey.cost }}</p>
      <div class="d-flex justify-content-between">
        <button class="btn btn-primary" @click="editJourney">Edit Journey</button>
        <button class="btn btn-danger" @click="deleteJourney">Delete Journey</button>
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
  methods: {
    editJourney() {
      this.$emit('edit-journey', this.journey);
    },
    deleteJourney() {
      this.$emit('delete-journey', this.journey.id);
    }
  }
}
</script>

<style scoped>
.saved-journey-item {
  cursor: pointer;
}
</style>