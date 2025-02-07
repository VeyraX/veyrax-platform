"use client"

import { Elements } from "@stripe/react-stripe-js"
import { loadStripe } from "@stripe/stripe-js"
import type { ReactNode } from "react"

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || "")

interface StripeProviderProps {
  children: ReactNode
  clientSecret: string
}

export function StripeProvider({ children, clientSecret }: StripeProviderProps) {
  return (
    <Elements 
      stripe={stripePromise} 
      options={{ 
        clientSecret,
        locale: 'en'
      }}
    >
      {children}
    </Elements>
  )
}

