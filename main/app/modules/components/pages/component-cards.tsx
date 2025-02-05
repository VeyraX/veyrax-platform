'use client'

import { useState } from 'react'
import ComponentCard from '../components/component-card'
import { dummyApiCards } from '../components-dummydata'
import { Button } from "@/components/ui/button"

export default function ComponentCards() {
  const [activeFilter, setActiveFilter] = useState('All')
  
  const allCategories = ['All', ...Array.from(new Set(dummyApiCards.flatMap(card => card.categories)))]

  const filteredCards = dummyApiCards.filter(card => 
    activeFilter === 'All' || card.categories.includes(activeFilter)
  )

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex flex-wrap gap-2">
        {allCategories.map((category) => (
          <Button
            key={category}
            variant={activeFilter === category ? "default" : "outline"}
            onClick={() => setActiveFilter(category)}
            className="rounded-full"
            size="sm"
          >
            {category}
          </Button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredCards.map((card) => (
          <ComponentCard key={card.id} {...card} />
        ))}
      </div>
    </div>
  )
}
