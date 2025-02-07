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
  const [isSuccess, setIsSuccess] = useState(false)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    if (!stripe || !elements) {
      return
    }

    setIsLoading(true)

    const { error } = await stripe.confirmPayment({
      elements,
      redirect: "if_required",
    })

    if (error) {
      setErrorMessage(error.message)
      setIsSuccess(false)
    } else {
      setIsSuccess(true)
      setErrorMessage("Payment successful!")
    }

    setIsLoading(false)
  }

  if (isSuccess) {
    return (
      <div className="text-center p-4">
        <div className="text-green-500 font-medium mb-2">✓ Payment successful!</div>
        <div className="text-sm text-muted-foreground">Thank you for your purchase</div>
      </div>
    )
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

