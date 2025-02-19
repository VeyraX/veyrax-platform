import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Search } from "lucide-react";
import { toolSuggestionsDummyData } from "./tool-suggestions-dummy-data";
import { getUserToolsClient } from "@/lib/utils/get-user-tools-client";

interface ToolSuggestionsProps {
  onSelect: (tool: { apiName: string; question: string }) => void;
  isOpen: boolean;
  searchQuery: string;
  userTools: Record<string, any>;
}

export function ToolSuggestionsCommand({ 
  onSelect, 
  isOpen, 
  searchQuery,
  userTools
}: ToolSuggestionsProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const availableSuggestions = toolSuggestionsDummyData.filter(tool => 
    tool.apiName in userTools
  );

  const filteredSuggestions = availableSuggestions.filter(tool =>
    tool.question.toLowerCase().includes(searchQuery.toLowerCase().slice(1)) ||
    tool.apiName.toLowerCase().includes(searchQuery.toLowerCase().slice(1))
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [isOpen, searchQuery]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => 
            prev <= 0 ? filteredSuggestions.length - 1 : prev - 1
          );
          break;
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => 
            prev >= filteredSuggestions.length - 1 ? 0 : prev + 1
          );
          break;
        case 'Enter':
          e.preventDefault();
          if (filteredSuggestions[selectedIndex]) {
            onSelect({ 
              ...filteredSuggestions[selectedIndex],
              question: filteredSuggestions[selectedIndex].question + ' '
            });
          }
          break;
        case 'Escape':
          e.preventDefault();
          onSelect({ apiName: '', question: '' });
          break;
      }
    };

    const selectedElement = document.querySelector(`[data-selected="true"]`);
    if (selectedElement) {
      setTimeout(() => {
        selectedElement.scrollIntoView({
          block: 'nearest',
          behavior: 'auto'
        });
      }, 0);
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, onSelect, filteredSuggestions]);

  const handleSelect = (tool: { apiName: string, question: string }) => {
    onSelect({
      ...tool,
      question: tool.question + ' '
    });
  };

  if (!isOpen) return null;
  if (!availableSuggestions.length) return null;

  return (
    <div className="flex h-full w-full flex-col overflow-hidden rounded-md bg-popover text-popover-foreground border shadow-md animate-in fade-in slide-in-from-bottom-2 duration-400">
      <div className="max-h-[300px] overflow-y-auto overflow-x-hidden p-1">
        {filteredSuggestions.length === 0 ? (
          <div className={cn(
            "relative flex cursor-default select-none items-center rounded-sm px-3 py-2.5 text-sm outline-none gap-3",
            "text-muted-foreground"
          )}>
            <span>No actions found.</span>
          </div>
        ) : (
          filteredSuggestions.map((tool, index) => (
            <div
              key={tool.apiName}
              className={cn(
                "relative flex cursor-pointer select-none items-center rounded-sm px-3 py-2.5 text-sm outline-none gap-3",
                "hover:bg-accent hover:text-accent-foreground",
                "data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground",
                selectedIndex === index && "bg-accent text-accent-foreground"
              )}
              onClick={() => handleSelect(tool)}
              data-selected={selectedIndex === index}
            >
              <img
                src={tool.logo}
                alt={`${tool.apiName} logo`}
                className="h-5 w-5 shrink-0"
              />
              <span>{tool.question}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}