"use server"

import Stripe from "stripe"

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2025-01-27.acacia",
})

export async function createPaymentIntent(amount: number) {
  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount,
      currency: "usd",
    })

    return { clientSecret: paymentIntent.client_secret }
  } catch (error) {
    console.error("Error creating PaymentIntent:", error)
    throw new Error("Failed to create PaymentIntent")
  }
}

