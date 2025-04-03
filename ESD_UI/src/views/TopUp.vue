<template>
    <div class="container">
        <div class="row">
            <div class="col-md-8 mx-auto">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h2 class="mb-0">Top Up Card</h2>
                    </div>
                    <div class="card-body">
                        <div class="card-details mb-4">
                            <h4>Card Details</h4>
                            <p>Card Number: {{ $route.query.cardNumber }}</p>
                            <p>Current Balance: ${{ Number($route.query.currentBalance).toFixed(2) }}</p>
                        </div>

                        <PaymentForm :cardId="$route.params.cardId" :userId="$route.query.userId"
                            :cardNumber="$route.query.cardNumber" :currentBalance="$route.query.currentBalance"
                            :phoneNumber="$route.query.phone_number" @payment-success="handlePaymentSuccess" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import PaymentForm from '@/components/PaymentForm.vue'

export default {
    name: 'TopUp',
    components: {
        PaymentForm
    },
    methods: {
        handlePaymentSuccess(result) {
            // Handle successful payment
            this.$router.push('/payment-success');
        }
    },
    created() {
        // Add validation for required parameters
        const requiredParams = ['cardId', 'userId', 'cardNumber', 'currentBalance'];
        const missingParams = requiredParams.filter(param => !this.$route.query[param] && !this.$route.params[param]);

        if (missingParams.length > 0) {
            console.error('Missing required parameters:', missingParams);
            this.$router.push('/profile');
        }
    }
}
</script>

<style scoped>
.container {
    min-height: calc(100vh - 120px);
    background: #f8fafc;
}

.card {
    border: none;
    border-radius: 15px;
    overflow: hidden;
}

.card-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
}

.card-header h2 {
    font-size: 1.5rem;
    font-weight: 600;
}

.card-body {
    padding: 2rem;
}

.card-details {
    background: #f8fafc;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}

.card-details h4 {
    color: #2d3748;
    font-weight: 600;
    margin-bottom: 1rem;
}

.detail-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #e2e8f0;
}

.detail-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
}

.detail-item label {
    color: #718096;
    font-weight: 500;
}

.detail-item span {
    color: #2d3748;
    font-weight: 600;
}
</style>