import { Check, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { AI_MODELS, ModelId } from "../api/models";
import { motion, AnimatePresence } from "framer-motion";

interface ModelSelectorProps {
  onModelSelect: (modelId: ModelId) => void;
  selectedModelId: ModelId;
  availableModels?: string[];
}

export function ModelSelector({ 
  onModelSelect, 
  selectedModelId,
  availableModels
}: ModelSelectorProps) {
  const selectedModel = AI_MODELS[selectedModelId];

  const getProviderIcon = (provider: string) => {
    const logoMap: Record<string, string> = {
      openai: '/models/openai.svg',
      anthropic: '/models/anthropic.svg',
      gemini: '/models/gemini.svg',
      openrouter: '/models/openai.svg'
    };
    
    return logoMap[provider] || logoMap.openai;
  };

  const isModelAvailable = (modelId: string) => {
    if (!availableModels) return true;
    return availableModels.includes(modelId);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="flex items-center justify-center gap-2 h-8 px-2 text-sm rounded-md hover:bg-black/10 dark:hover:bg-white/10 focus-visible:ring-0 focus-visible:ring-offset-0"
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedModelId}
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 5 }}
              transition={{ duration: 0.15 }}
              className="flex items-center gap-2"
            >
              <img 
                src={getProviderIcon(selectedModel.originalProvider)} 
                alt={selectedModel.originalProvider}
                className="w-5 h-5"
              />
              {selectedModel.name}
              {selectedModel.isPremium && !isModelAvailable(selectedModelId) && (
                <Lock className="w-4 h-4 opacity-70" />
              )}
            </motion.div>
          </AnimatePresence>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        className={cn(
          "min-w-[12rem]",
          "border-black/10 dark:border-white/10",
          "bg-white dark:bg-neutral-900"
        )}
      >
        <TooltipProvider>
          {Object.entries(AI_MODELS).map(([modelId, model]) => {
            const isAvailable = isModelAvailable(modelId);
            const isPremium = model.isPremium && !isAvailable;
            
            return (
              <div key={modelId}>
                {isPremium ? (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="px-3 py-2 text-sm flex items-center justify-between gap-2 opacity-60 cursor-not-allowed">
                        <div className="flex items-center gap-2">
                          <img 
                            src={getProviderIcon(model.originalProvider)} 
                            alt={model.originalProvider}
                            className="w-5 h-5" 
                          />
                          <span className="flex items-center gap-1.5">
                            {model.name}
                            <Lock className="w-4 h-4" />
                          </span>
                        </div>
                        {selectedModelId === modelId && (
                          <Check className="w-5 h-5" />
                        )}
                      </div>
                    </TooltipTrigger>
                    <TooltipContent side="right" className="text-sm">
                      <p>Set your own API key or upgrade subscription</p>
                    </TooltipContent>
                  </Tooltip>
                ) : (
                  <DropdownMenuItem
                    onSelect={() => onModelSelect(modelId as ModelId)}
                    className="flex items-center justify-between gap-2 px-3 py-2 text-sm"
                  >
                    <div className="flex items-center gap-2">
                      <img 
                        src={getProviderIcon(model.originalProvider)} 
                        alt={model.originalProvider}
                        className="w-5 h-5" 
                      />
                      <span className="flex items-center gap-1.5">
                        {model.name}
                      </span>
                    </div>
                    {selectedModelId === modelId && (
                      <Check className="w-5 h-5" />
                    )}
                  </DropdownMenuItem>
                )}
              </div>
            );
          })}
        </TooltipProvider>
      </DropdownMenuContent>
    </DropdownMenu>
  );
} 