import { useState, useEffect } from "react"

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(
    typeof window !== "undefined" ? window.matchMedia(query).matches : false
  )

  useEffect(() => {
    if (typeof window === "undefined") return undefined

    const mediaQuery = window.matchMedia(query)
    
    const updateMatches = () => setMatches(mediaQuery.matches)
    
    mediaQuery.addEventListener("change", updateMatches)
    
    return () => mediaQuery.removeEventListener("change", updateMatches)
  }, [query])

  return matches
}