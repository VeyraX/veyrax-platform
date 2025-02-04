"use client"

import { useState } from "react"
import { useStripe, useElements, PaymentElement } from "@stripe/react-stripe-js"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

export function PaymentForm() {
  const stripe = useStripe()
  const elements = useElements()
  const [errorMessage, setErrorMessage] = useState<string | undefined>()
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    if (!stripe || !elements) {
      return
    }

    setIsLoading(true)

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/payment-confirmation`,
      },
    })

    if (error) {
      setErrorMessage(error.message)
    }

    setIsLoading(false)
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Payment Details</CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent>
          <PaymentElement />
        </CardContent>
        <CardFooter>
          <Button type="submit" disabled={!stripe || isLoading} className="w-full">
            {isLoading ? "Processing..." : "Pay Now"}
          </Button>
        </CardFooter>
      </form>
      {errorMessage && <div className="text-red-500 text-center mt-4">{errorMessage}</div>}
    </Card>
  )
}

