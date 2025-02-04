'use client'

import { FC } from 'react'
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Heart, ArrowUpRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ApiCardProps } from './component-types'
import { useRouter } from 'next/navigation'

const ComponentCard: FC<ApiCardProps> = (props) => {
  const router = useRouter()

  const handleClick = () => {
    router.push(`/api/${props.provider_tag}`)
  }

  return (
    <Card className="w-full border shadow-none rounded-lg h-[204px]">
      <CardContent className="p-4 h-full flex flex-col">
        <div className="flex flex-col gap-3 flex-1">
          <div className="flex justify-between items-center">
            <img 
              src={props.logo || '/default-logo.svg'} 
              alt={props.name} 
              width={36} 
              height={36} 
              className="rounded-lg object-contain w-[36px] h-[36px] p-[3px]"
              onError={(e) => {
                e.currentTarget.src = '/default-logo.svg'
              }}
            />
            <Button variant="ghost" size="sm">
              <Heart className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-semibold truncate">{props.name}</h2>
            <p className="text-muted-foreground mt-1 text-sm line-clamp-2">{props.description}</p>
          </div>
        </div>

        <div className="flex justify-between items-center mt-3 pt-3">
          <div className="flex gap-1 flex-wrap">
            {props.categories.map((category, index) => (
              <Badge key={index} variant="outline" className="rounded text-xs">
                {category}
              </Badge>
            ))}
          </div>
          <Button variant="outline" size="sm" onClick={handleClick}>
            <ArrowUpRight className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default ComponentCard

