<template>
  <div class="container mt-5">
    <h1 class="mb-4">Test Payment Integration</h1>
    <PaymentForm @payment-success="handlePaymentSuccess" />
  </div>
</template>

<script>
import PaymentForm from '@/components/PaymentForm.vue'

export default {
  name: 'TestPayment',
  components: {
    PaymentForm
  },
  methods: {
    handlePaymentSuccess(paymentIntent) {
      console.log('Payment successful:', paymentIntent)
    }
  }
}
</script> 