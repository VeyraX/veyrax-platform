'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { getPublicTemplates, getTemplateActions } from '../../../flows/api/api.flows'
import { UserFlow, ProviderAction } from '../../../flows/api/types.flows'
import FlowCard, { FlowSkeleton } from '../../../flows/components/view/flow-card'
import Link from 'next/link'
import { InfiniteSlider } from '@/components/ui/infinite-slider'
import Particles from "@/components/ui/particles"
import { useTheme } from "next-themes"

interface TemplateWithTools extends UserFlow {
  tools?: ProviderAction[];
}

const UseCases = () => {
  const [templates, setTemplates] = useState<TemplateWithTools[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { resolvedTheme } = useTheme()
  const [color, setColor] = useState("#ffffff")

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000")
  }, [resolvedTheme])

  useEffect(() => {
    fetchTemplates()
  }, [])

  // Add mask-sides style
  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = `
      .mask-sides {
        mask-image: linear-gradient(to right, transparent, black 5%, black 95%, transparent);
        -webkit-mask-image: linear-gradient(to right, transparent, black 5%, black 95%, transparent);
      }
    `
    document.head.appendChild(style)

    return () => {
      document.head.removeChild(style)
    }
  }, [])

  const fetchTemplates = async () => {
    setIsLoading(true)
    try {
      const templatesData = await getPublicTemplates()
      
      const templateIds = templatesData.map(template => template.id)
      const templateActionsPromises = templateIds.map(id => getTemplateActions(id))
      const templateActionsResults = await Promise.all(templateActionsPromises)
      
      const flowToolsMap = new Map()
      templateActionsResults.forEach((actions, index) => {
        const templateId = templateIds[index]
        const uniqueProviders = new Map()
        
        actions.forEach(tool => {
          if (!uniqueProviders.has(tool.provider_id)) {
            uniqueProviders.set(tool.provider_id, tool)
          }
        })
        
        flowToolsMap.set(templateId, Array.from(uniqueProviders.values()))
      })

      const templatesWithTools = templatesData.map(template => ({
        ...template,
        tools: flowToolsMap.get(template.id) || []
      }))

      // Sort templates by date created
      const sortedTemplates = [...templatesWithTools].sort((a, b) => {
        return new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime()
      })
      
      setTemplates(sortedTemplates)
    } catch (error) {
      console.error('Failed to fetch templates:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Разделяем шаблоны на три группы
  const splitTemplates = (templates: TemplateWithTools[]) => {
    // Если шаблонов недостаточно, дублируем их
    let workingTemplates = [...templates]
    while (workingTemplates.length < 15) {
      workingTemplates = [...workingTemplates, ...templates]
    }
    
    // Создаем три группы с примерно равным количеством шаблонов
    const third = Math.ceil(workingTemplates.length / 3)
    return [
      workingTemplates.slice(0, third),
      workingTemplates.slice(0, third), // Используем те же шаблоны для всех рядов
      workingTemplates.slice(0, third)
    ]
  }

  const templateGroups = isLoading ? [[], [], []] : splitTemplates(templates)

  // Функция для рендера карточек-заглушек
  const renderSkeletons = () => {
    return [...Array(8)].map((_, index) => (
      <div key={`skeleton-${index}`} style={{width: '320px'}}>
        <FlowSkeleton />
      </div>
    ))
  }

  return (
    <div className="w-full py-20 overflow-hidden">
      <div className="container mx-auto px-4 md:px-8">
        <div className="flex gap-8 items-center justify-center flex-col relative">
          <Particles
            className="absolute inset-0"
            quantity={100}
            ease={80}
            color={color}
            refresh
          />
          
          <div className="flex gap-4 flex-col items-center">
            <div className="flex flex-col items-center gap-3">
              <h2 className="text-5xl md:text-7xl max-w-3xl tracking-tighter text-center">
                <span className="font-regular">Pre-built</span> <span className="font-semibold">flow templates</span>
              </h2>
            </div>

            <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center">
              Copy and customize dozen of templates in just one click. Leverage AI to automate any task with 70+ integrations.{" "}
            </p>
          </div>
        </div>

        <div className="mb-6 mt-12">
          <InfiniteSlider 
            duration={80}
            gap={24}
            className="py-2 mask-sides"
          >
            {isLoading ? renderSkeletons() : 
              templateGroups[0].map((template, index) => (
                <div key={`row1-${template.id}-${index}`} style={{width: '320px'}}>
                  <FlowCard
                    {...template}
                    flowTools={template.tools || []}
                  />
                </div>
              ))
            }
          </InfiniteSlider>
        </div>

        <div className="mb-6">
          <InfiniteSlider 
            duration={80}
            gap={24}
            reverse={true}
            className="py-2 mask-sides"
          >
            {isLoading ? renderSkeletons() : 
              templateGroups[1].map((template, index) => (
                <div key={`row2-${template.id}-${index}`} style={{width: '320px'}}>
                  <FlowCard
                    {...template}
                    flowTools={template.tools || []}
                  />
                </div>
              ))
            }
          </InfiniteSlider>
        </div>

        <div className="mb-6">
          <InfiniteSlider 
            duration={80}
            gap={24}
            className="py-2 mask-sides"
          >
            {isLoading ? renderSkeletons() : 
              templateGroups[2].map((template, index) => (
                <div key={`row3-${template.id}-${index}`} style={{width: '320px'}}>
                  <FlowCard
                    {...template}
                    flowTools={template.tools || []}
                  />
                </div>
              ))
            }
          </InfiniteSlider>
        </div>

        <div className="flex justify-center mt-10">
          <Link href="/flows">
            <Button variant="outline" size="lg">
              View all templates
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default UseCases
