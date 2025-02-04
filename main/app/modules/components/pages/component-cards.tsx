'use client'

import { FC } from 'react'
import ComponentCard from '../components/component-card'
import { dummyApiCards } from '../components-dummydata'

export default function ComponentCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-6">
      {dummyApiCards.map((card) => (
        <ComponentCard key={card.id} {...card} />
      ))}
    </div>
  )
}
