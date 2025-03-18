<template>
  <div class="payment-success-container">
    <div class="card">
      <div class="card-body text-center">
        <div class="success-icon mb-4">
          <i class="bi bi-check-circle-fill text-success" style="font-size: 4rem;"></i>
        </div>
        <h2 class="card-title mb-4">Payment Successful!</h2>
        <p class="card-text mb-4">Thank you for your payment. Your transaction has been completed successfully.</p>
        <div class="transaction-details mb-4" v-if="paymentIntent">
          <p class="mb-2"><strong>Transaction ID:</strong> {{ paymentIntent.id }}</p>
          <p class="mb-2"><strong>Amount:</strong> ${{ (paymentIntent.amount / 100).toFixed(2) }}</p>
          <p class="mb-2"><strong>Status:</strong> {{ paymentIntent.status }}</p>
        </div>
        <button @click="goHome" class="btn btn-primary">
          Return to Home
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PaymentSuccess',
  data() {
    return {
      paymentIntent: null
    }
  },
  created() {
    // Get payment details from route state or Vuex store if available
    if (this.$route.state?.paymentIntent) {
      this.paymentIntent = this.$route.state.paymentIntent;
    }
  },
  methods: {
    goHome() {
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
.payment-success-container {
  max-width: 500px;
  margin: 4rem auto;
  padding: 0 1rem;
}

.card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: none;
  border-radius: 8px;
}

.card-title {
  color: #2d3748;
  font-weight: 600;
}

.transaction-details {
  background-color: #f7fafc;
  padding: 1rem;
  border-radius: 4px;
  text-align: left;
}

.btn-primary {
  background-color: #4299e1;
  border-color: #4299e1;
  padding: 0.75rem 2rem;
  font-weight: 500;
}

.btn-primary:hover {
  background-color: #3182ce;
  border-color: #3182ce;
}
</style> 