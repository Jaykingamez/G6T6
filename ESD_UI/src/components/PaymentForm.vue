<template>
  <div class="payment-container">
    <div class="card">
      <div class="card-body">
        <h2 class="card-title mb-4">Payment Details</h2>
        <div class="mb-3">
          <label for="amount" class="form-label">Amount (SGD)</label>
          <div class="input-group">
            <span class="input-group-text">$</span>
            <input 
              type="number" 
              id="amount" 
              v-model="amount" 
              class="form-control" 
              min="1" 
              step="0.01"
              :disabled="processing"
            >
          </div>
        </div>
        
        <div id="card-element" class="form-control mb-3"></div>
        <div id="card-errors" class="alert alert-danger" role="alert" v-if="errorMessage">
          {{ errorMessage }}
        </div>
        
        <button 
          @click="handlePayment" 
          class="btn btn-primary w-100"
          :disabled="processing"
        >
          <span v-if="processing" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          {{ processing ? 'Processing...' : 'Pay Now' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { loadStripe } from '@stripe/stripe-js';
import axios from 'axios';

const stripePromise = loadStripe(process.env.VUE_APP_STRIPE_PUBLISHABLE_KEY);

export default {
  name: 'PaymentForm',
  data() {
    return {
      stripe: null,
      elements: null,
      card: null,
      amount: 10,
      processing: false,
      errorMessage: '',
    };
  },
  async mounted() {
    try {
      this.stripe = await stripePromise;
      this.elements = this.stripe.elements();
      this.card = this.elements.create('card', {
        style: {
          base: {
            fontSize: '16px',
            color: '#424770',
            '::placeholder': {
              color: '#aab7c4',
            },
          },
          invalid: {
            color: '#9e2146',
          },
        },
      });
      this.card.mount('#card-element');

      this.card.on('change', (event) => {
        this.errorMessage = event.error ? event.error.message : '';
      });
    } catch (error) {
      console.error('Error initializing Stripe:', error);
      this.errorMessage = 'Failed to initialize payment system. Please try again later.';
    }
  },
  methods: {
    async handlePayment() {
      if (!this.amount || this.amount <= 0) {
        this.errorMessage = 'Please enter a valid amount';
        return;
      }

      this.processing = true;
      this.errorMessage = '';

      try {
        console.log('Sending payment request...'); // Debug log
        const response = await axios.post('http://127.0.0.1:5008/makepayment', {
          amount: Math.round(this.amount * 100), // Convert to cents
        });

        const { clientSecret } = response.data;

        // Confirm the payment
        const result = await this.stripe.confirmCardPayment(clientSecret, {
          payment_method: {
            card: this.card,
          },
        });

        if (result.error) {
          this.errorMessage = result.error.message;
        } else {
          this.$emit('payment-success', result.paymentIntent);
          this.$router.push('/payment-success');
        }
      } catch (error) {
        console.error('Payment error:', error);
        this.errorMessage = error.response?.data?.error || 'An error occurred. Please try again.';
      } finally {
        this.processing = false;
      }
    },
  },
};
</script>

<style scoped>
.payment-container {
  max-width: 500px;
  margin: 2rem auto;
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

#card-element {
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background-color: white;
}

.form-control:focus {
  border-color: #4299e1;
  box-shadow: 0 0 0 0.2rem rgba(66, 153, 225, 0.25);
}

.btn-primary {
  background-color: #4299e1;
  border-color: #4299e1;
  padding: 0.75rem;
  font-weight: 500;
}

.btn-primary:hover:not(:disabled) {
  background-color: #3182ce;
  border-color: #3182ce;
}

.btn-primary:disabled {
  background-color: #a0aec0;
  border-color: #a0aec0;
  cursor: not-allowed;
}

.alert-danger {
  background-color: #fff5f5;
  border-color: #feb2b2;
  color: #c53030;
}
</style> 