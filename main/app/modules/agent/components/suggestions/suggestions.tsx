"use client"

import { Card } from "@/components/ui/card"
import { motion } from "framer-motion"

export function Suggestions({
  items,
  onSelect,
  visible
}: {
  items: { title: string; subtitle: string; query: string }[]
  onSelect: (query: string) => void
  visible: boolean
}) {
  if (!visible) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 w-full">
        {items.map((item, index) => (
          <Card
            key={index}
            className="p-3 cursor-pointer hover:bg-muted/30 transition-all 
                      duration-200 group border border-gray-200 rounded-md
                      hover:-translate-y-0.5 h-full"
            onClick={() => onSelect(item.query)}
          >
            <div className="flex flex-col space-y-0.5">
              <h3 className="text-sm font-medium text-foreground/90 leading-tight line-clamp-1">
                {item.title}
              </h3>
              <p className="text-xs text-muted-foreground/80 leading-tight line-clamp-1">
                {item.subtitle}
              </p>
            </div>
          </Card>
        ))}
      </div>

    </motion.div>
  )
}