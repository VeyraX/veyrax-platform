"use client"

import * as React from "react"
import { Check, ChevronsUpDown, PencilRuler } from "lucide-react"
import Image from "next/image"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

import { dummyApiCards } from "@/app/modules/components/components-dummydata"

export function ToolSelector() {
  const [open, setOpen] = React.useState(false)
  const [selectedValues, setSelectedValues] = React.useState<string[]>([])

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button 
          variant="ghost" 
          role="combobox" 
          aria-expanded={open} 
          className={cn(
            "w-[120px] justify-start h-9 bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 text-black/40 dark:text-white/40 hover:text-black dark:hover:text-white transition-all duration-200",
            selectedValues.length > 0 && "w-full"
          )}
        >
          <SelectedItems selectedValues={selectedValues} />
          <ChevronsUpDown className="ml-auto h-4 w-4 shrink-0" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0">
        <Command>
          <CommandInput placeholder="Search tools..." />
          <CommandList>
            <CommandEmpty>No tool found.</CommandEmpty>
            <CommandGroup>
              {dummyApiCards.map((tool) => (
                <CommandItem
                  key={tool.id}
                  onSelect={() => {
                    setSelectedValues((prev) =>
                      prev.includes(tool.id) ? prev.filter((id) => id !== tool.id) : [...prev, tool.id],
                    )
                    setOpen(false)
                  }}
                >
                  <Check
                    className={cn("mr-2 h-4 w-4", selectedValues.includes(tool.id) ? "opacity-100" : "opacity-0")}
                  />
                  <Image
                    src={tool.logo || ''}
                    alt={`${tool.name} logo`}
                    width={20}
                    height={20}
                    className="h-5 w-5"
                  />
                  <span className="ml-2">{tool.name}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

function SelectedItems({ selectedValues }: { selectedValues: string[] }) {
  if (selectedValues.length === 0) {
    return (
      <div className="flex items-center">
        <PencilRuler className="h-4 w-4 mr-2" />
        <span>Auto</span>
      </div>
    )
  }

  const displayedItems = selectedValues.slice(0, 4)
  const remainingCount = selectedValues.length - displayedItems.length

  return (
    <div className="flex items-center space-x-2 overflow-hidden">
      {displayedItems.map((id) => {
        const tool = dummyApiCards.find((t) => t.id === id)
        return tool ? (
          <div key={id} className="flex items-center">
            <Image
              src={tool.logo || ''}
              alt={`${tool.name} logo`}
              width={20}
              height={20}
              className="h-5 w-5"
            />
          </div>
        ) : null
      })}
      {remainingCount > 0 && <span className="text-sm text-muted-foreground">{`+${remainingCount}`}</span>}
    </div>
  )
}
