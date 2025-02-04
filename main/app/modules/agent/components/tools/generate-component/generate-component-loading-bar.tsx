"use client"

import { useEffect, useState } from "react"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardContent } from "@/components/ui/card"

 interface ProgressState {
    description: string
    progress: number
  }

export default function ProgressStates({ progressStates, title }: { progressStates: ProgressState[], title: string }) {
  const [currentState, setCurrentState] = useState<ProgressState>(progressStates[0])
  const [isFinished, setIsFinished] = useState(false)
  const [dots, setDots] = useState('')

  useEffect(() => {
    const dotInterval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.')
    }, 500)

    return () => clearInterval(dotInterval)
  }, [])

  useEffect(() => {
    let currentIndex = 0

    const nextStep = () => {
      if (currentIndex < progressStates.length - 1) {
        currentIndex++
        setCurrentState(progressStates[currentIndex])
        const randomDuration = Math.floor(Math.random() * (12000 - 5000 + 1) + 5000)
        setTimeout(nextStep, randomDuration)
      } else {
        setIsFinished(true)
      }
    }

    const initialDuration = Math.floor(Math.random() * (12000 - 5000 + 1) + 5000)
    const initialTimeout = setTimeout(nextStep, initialDuration)

    return () => clearTimeout(initialTimeout)
  }, [progressStates])

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <h3 className="text-xl font-semibold tracking-tight">{title}</h3>
      </CardHeader>
      <CardContent>
        {!isFinished ? (
          <>
            <div className="mb-4">
              <div className="flex justify-between items-center">
                <p className="text-sm text-muted-foreground">
                  {currentState.description}
                  <span className="inline-block w-6">{dots}</span>
                </p>
                <span className="text-sm font-medium">{currentState.progress}%</span>
              </div>
            </div>
            <Progress value={currentState.progress} className="h-2 mb-4" />
          </>
        ) : (
          <Button 
            className="w-full" 
            onClick={() => window.open('/components/eventbright', '_blank')}
          >
            Open Component
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

