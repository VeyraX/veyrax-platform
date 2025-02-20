"use client"

import type React from "react"
import { useRef, useEffect } from "react"

interface AudioWaveformProps {
  isRecording: boolean
  isPaused?: boolean
  className?: string
}

export const AudioWaveform: React.FC<AudioWaveformProps> = ({ isRecording, isPaused, className }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  const analyserRef = useRef<AnalyserNode | null>(null)
  const dataArrayRef = useRef<number[]>([])

  useEffect(() => {
    if (isRecording) {
      startVisualization()
    } else {
      stopVisualization()
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isRecording])

  const startVisualization = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const audioContext = new AudioContext()
      const source = audioContext.createMediaStreamSource(stream)
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 128
      source.connect(analyser)
      analyserRef.current = analyser
      dataArrayRef.current = []
      drawScrollingBars()
    } catch (error) {
      console.error("Error accessing microphone:", error)
    }
  }

  const stopVisualization = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
    }
    resetCanvas()
  }

  const resetCanvas = () => {
    if (!canvasRef.current) return
    const ctx = canvasRef.current.getContext("2d")
    if (!ctx) return

    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)

    ctx.beginPath()
    ctx.strokeStyle = "rgba(0, 0, 0, 0.1)"
    ctx.lineWidth = 2
    const y = canvasRef.current.height / 2
    ctx.moveTo(0, y)
    ctx.lineTo(canvasRef.current.width, y)
    ctx.stroke()
  }

  const drawScrollingBars = () => {
    if (!canvasRef.current || !analyserRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const analyser = analyserRef.current
    const bufferLength = analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)
    const barWidth = 2
    const gap = 1
    let frameCount = 0

    // Получаем текущую тему из localStorage
    const isDarkTheme = localStorage.getItem('theme') === 'dark'

    const draw = () => {
      if (!isPaused) {
        animationRef.current = requestAnimationFrame(draw)
        
        frameCount++
        if (frameCount % 3 === 0) {
          analyser.getByteFrequencyData(dataArray)
          const average = Array.from(dataArray).reduce((a, b) => a + b, 0) / bufferLength
          dataArrayRef.current.unshift(average)
        }

        ctx.clearRect(0, 0, canvas.width, canvas.height)

        ctx.beginPath()
        ctx.strokeStyle = isDarkTheme ? "rgba(255, 255, 255, 0.1)" : "rgba(0, 0, 0, 0.1)"
        ctx.lineWidth = 2
        const baselineY = canvas.height / 2
        ctx.moveTo(0, baselineY)
        ctx.lineTo(canvas.width, baselineY)
        ctx.stroke()

        const totalBars = Math.floor(canvas.width / (barWidth + gap))

        dataArrayRef.current.slice(0, totalBars).forEach((value, index) => {
          const x = canvas.width - (index * (barWidth + gap)) - barWidth
          const normalizedValue = (value / 128) * 1.5
          const barHeight = Math.max(3, normalizedValue * (canvas.height / 1.5))

          ctx.fillStyle = isDarkTheme ? "rgba(255, 255, 255, 0.4)" : "rgba(0, 0, 0, 0.4)"
          ctx.fillRect(x, baselineY - barHeight / 2, barWidth, barHeight)
        })

        if (dataArrayRef.current.length > totalBars * 2) {
          dataArrayRef.current = dataArrayRef.current.slice(0, totalBars)
        }
      }
    }

    resetCanvas()
    draw()
  }

  return (
    <div className={className}>
      <canvas 
        ref={canvasRef} 
        width={800} 
        height={100} 
        className="w-full h-full rounded-xl rounded-b-none bg-black/5 dark:bg-white/5"
      />
    </div>
  )
}