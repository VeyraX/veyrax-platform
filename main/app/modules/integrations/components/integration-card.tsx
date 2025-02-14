'use client'

import { FC } from 'react'
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { IntegrationCardProps } from '../api/types.integrations'
import { useRouter } from 'next/navigation'

export const IntegrationCard: FC<IntegrationCardProps> = (props) => {
  const router = useRouter()

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
            {props.connected && (
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                Connected
              </Badge>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-semibold truncate">{props.name}</h2>
            <p className="text-muted-foreground mt-1 text-sm line-clamp-2">{props.description}</p>
          </div>
        </div>

        <div className="flex items-center mt-3 pt-3 justify-end">
          <Button 
            variant={props.connected ? "secondary" : "outline"}
            size="sm" 
            onClick={() => router.push(`/components/${props.provider_tag}`)}
          >
            {props.connected ? (
              <>
                <ArrowUpRight className="h-4 w-4" /> Manage
              </>
            ) : (
              <>
                <Plus className="h-4 w-4" /> Connect
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}