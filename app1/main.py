#! /usr/bin/env python3.6
# Python 3.6 or newer required.

import json
import os
import stripe
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stripe.api_key = os.getenv('STRIPE_API_KEY')
endpoint_secret = os.getenv('ENDPOINT_SECRET')
# This is your test secret API key.
# stripe.api_key = 'sk_test_51R2ZQrJeAtLoMNXrspahfMSPaE5uXm3rINc5PI7fLCNiQ1YDmQHijVBFPaD1zzvXSJNoGn0hGYOL718NUtgp5SfM00v6CGYJpm'

# Replace this endpoint secret with your endpoint's unique secret
# If you are testing with the CLI, find the secret by running 'stripe listen'
# If you are using an endpoint defined with the API or dashboard, look in your webhook settings
# at https://dashboard.stripe.com/webhooks
# endpoint_secret = 'whsec_4bf549624d8a635413af3157cc5fb44eea3c06da07390f55c285d45e3b25de64'
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data

    try:
        event = json.loads(payload)
    except json.decoder.JSONDecodeError as e:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return jsonify(success=False)
    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return jsonify(success=False)

    # Handle the event
    if event and event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        logger.info('Payment for {} succeeded'.format(payment_intent['amount']))
        logger.info(f'Full payment intent data: {payment_intent}')
    elif event['type'] == 'payment_method.attached':
        payment_method = event['data']['object']
        logger.info(f'Payment method attached: {payment_method}')
    else:
        # Unexpected event type
        logger.info('Unhandled event type {}'.format(event['type']))
        
    # if event and event['type'] == 'payment_intent.succeeded':
    #     payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
    #     print('Payment for {} succeeded'.format(payment_intent['amount']))
    #     # Then define and call a method to handle the successful payment intent.
    #     # handle_payment_intent_succeeded(payment_intent)
    # elif event['type'] == 'payment_method.attached':
    #     payment_method = event['data']['object']  # contains a stripe.PaymentMethod
    #     # Then define and call a method to handle the successful attachment of a PaymentMethod.
    #     # handle_payment_method_attached(payment_method)
    # else:
    #     # Unexpected event type
    #     print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4243, debug=True)