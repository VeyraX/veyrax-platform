import React from "react";
import { Bot } from "lucide-react";
import { AIInputWithSearch } from "../components/input/ai-input";
import { Suggestions } from "../components/suggestions /suggestions"
import { SuggestionsDummyAgent } from "../components/suggestions /suggestions-dummy"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";

interface AssistantEmptyStateProps {
  onSubmit: (message: string) => void;
  isLoading?: boolean;
  onStop?: () => void;
}

export function AssistantEmptyState({ onSubmit, isLoading, onStop }: AssistantEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <div className="flex-1 flex flex-col items-center justify-center max-w-3xl w-full px-4">
        <h1 className="text-3xl font-bold mb-12">How can I help you today, Dmitry?</h1>
        
        <div className="w-full space-y-8">
          <AIInputWithSearch
            placeholder="What do you want to know?"
            onSubmit={onSubmit}
            className="max-w-none"
            isLoading={isLoading}
            onStop={onStop}
          />
          
          <ScrollArea className="w-full whitespace-nowrap">
            <div className="flex space-x-4 pb-4">
              {SuggestionsDummyAgent.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => onSubmit(suggestion.query)}
                  className="inline-flex items-center px-4 py-2 rounded-full 
                    bg-muted/60 hover:bg-muted/80 transition-colors
                    text-sm whitespace-nowrap"
                >
                  {suggestion.title}
                </button>
              ))}
            </div>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>
        </div>
      </div>
    </div>
  );
}