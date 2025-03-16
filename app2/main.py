# This example sets up an endpoint using the Flask framework.
# Watch this video to get started: https://youtu.be/7Ul1vfmsDck.

import os
import stripe

from flask import Flask, request, render_template_string

app = Flask(__name__)

stripe.api_key = os.getenv('STRIPE_API_KEY')
# endpoint_secret = os.getenv('ENDPOINT_SECRET')

# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
# stripe.api_key = 'sk_test_51R2ZQrJeAtLoMNXrspahfMSPaE5uXm3rINc5PI7fLCNiQ1YDmQHijVBFPaD1zzvXSJNoGn0hGYOL718NUtgp5SfM00v6CGYJpm'

@app.route('/order/success', methods=['GET'])
def order_success():
  session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
  print(session)
  customer = session.customer_details.name

  return render_template_string('<html><body><h1>Thanks for your order, {{customer}}!</h1></body></html>', customer=customer)

if __name__== '__main__':
  app.run(host='0.0.0.0', port=4242, debug=True)