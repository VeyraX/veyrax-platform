"use client";

import { Card, CardContent } from "@/components/ui/card";
import { ExternalLink } from "lucide-react";
import { inspirationItems } from "../../api/deploy-view-dummy-data";

export function McpRegistry() {
  return (
    <div className="w-full mt-16">
      <h2 className="text-2xl font-medium mb-6">MCP Registry</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {inspirationItems.map((item) => (
          <Card 
            key={item.name} 
            className="shadow-none rounded-lg hover:border-primary/50 hover:bg-secondary/50 transition-all cursor-pointer group" 
            onClick={() => window.open(item.url, '_blank')}
          >
            <CardContent className="p-3">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-sm">{item.name}</h3>
                <ExternalLink className="h-3.5 w-3.5 text-muted-foreground/50 group-hover:text-foreground group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
} 