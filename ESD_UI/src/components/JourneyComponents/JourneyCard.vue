<template>
  <div class="journey-card">
    <div class="card">
      <div class="card-body">
        <h5 class="card-title">{{ transportMode }}</h5>
        <p class="card-text">Estimated Travel Time: {{ travelTime }} minutes</p>
        <p class="card-text">Cost: ${{ cost }}</p>
        <div class="d-flex justify-content-between">
          <button class="btn btn-primary" @click="saveJourney">Save Journey</button>
          <button class="btn btn-secondary" @click="viewOnMap">View on Map</button>
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
      type: Number,
      required: true
    }
  },
  methods: {
    saveJourney() {
      // Logic to save the journey
      this.$emit('save-journey', { transportMode: this.transportMode, travelTime: this.travelTime, cost: this.cost });
    },
    viewOnMap() {
      // Logic to view the journey on a map
      this.$emit('view-on-map', { transportMode: this.transportMode });
    }
  }
}
</script>

<style scoped>
.journey-card {
  margin: 10px;
}
.card {
  width: 100%;
}
</style>