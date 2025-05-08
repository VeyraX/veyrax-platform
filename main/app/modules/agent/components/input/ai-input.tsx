"use client";

import { Globe, Paperclip, ArrowUp, Mic, Square } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { Textarea } from "@/components/ui/textarea";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { useAutoResizeTextarea } from "@/hooks/use-auto-resize-textarea";
import { Button } from "@/components/ui/button";
import { CircleStop } from "lucide-react";
import { AudioWaveform } from "./audio-input"
import React from "react";
import { AIModel, AI_MODELS, getDefaultModel, ModelId } from "../api/models";
import { ModelSelector } from "./model-selector";

interface AIInputWithSearchProps {
  id?: string;
  placeholder?: string;
  minHeight?: number;
  maxHeight?: number;
  onSubmit?: (value: string, modelId?: ModelId) => void;
  onFileSelect?: (file: File) => void;
  onVoiceText?: (text: string) => void;
  onModelChange?: (modelId: ModelId) => void;
  className?: string;
  isLoading?: boolean;
  onStop?: () => void;
  onShowSuggestions?: (show: boolean) => void;
  userTools: Record<string, any>;
  initialInput?: string | null;
  value?: string;
  onChange?: (value: string) => void;
  availableModels?: string[];
  defaultModelId?: ModelId;
}

export const AIInputWithSearch = React.forwardRef<HTMLTextAreaElement, AIInputWithSearchProps>(({
  id = "ai-input-with-search",
  placeholder = "Ask anything...",
  minHeight = 64,
  maxHeight = 256,
  onSubmit,
  onFileSelect,
  onVoiceText,
  onModelChange,
  className,
  isLoading,
  onStop,
  onShowSuggestions,
  userTools,
  initialInput = null,
  value: controlledValue,
  onChange,
  availableModels,
  defaultModelId,
}, ref) => {
  const [internalValue, setInternalValue] = useState(initialInput || "");
  const value = controlledValue !== undefined ? controlledValue : internalValue;
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight,
    maxHeight,
  });
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [isProcessingAudio, setIsProcessingAudio] = useState(false);
  const [selectedModelId, setSelectedModelId] = useState<ModelId>(
    defaultModelId || getDefaultModel().id as ModelId
  );

  React.useImperativeHandle(ref, () => textareaRef.current as HTMLTextAreaElement);

  useEffect(() => {
    if (defaultModelId) {
      setSelectedModelId(defaultModelId);
    }
  }, [defaultModelId]);

  React.useEffect(() => {
    if (initialInput && !value) {
      setInternalValue(initialInput);
      adjustHeight();
    }
  }, [initialInput, value, adjustHeight]);

  const handleSubmit = () => {
    const trimmedValue = value.trim();
    if (trimmedValue) {
      onSubmit?.(trimmedValue, selectedModelId);
      if (controlledValue === undefined) {
        setInternalValue("");
      }
      textareaRef.current?.style.height && 
        (textareaRef.current.style.height = `${minHeight}px`);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect?.(file);
    }
  };

  const handleVoiceResponse = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);

      const response = await fetch('/api/voice', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      if (data.text) {
        setInternalValue(data.text);
        onVoiceText?.(data.text);
        adjustHeight();
      }
    } catch (error) {
      console.error('Error processing voice:', error);
    } finally {
      setIsProcessingAudio(false);
      setIsRecording(false);
    }
  };

  const handleMediaRecorder = async () => {
    const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
    chunksRef.current = [];
    setIsProcessingAudio(true);
    await handleVoiceResponse(audioBlob);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        await handleMediaRecorder();
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Error accessing microphone:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    if (onChange) {
      onChange(newValue);
    } else {
      setInternalValue(newValue);
    }
    
    onShowSuggestions?.(true);
    
    adjustHeight();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleModelSelect = (modelId: ModelId) => {
    setSelectedModelId(modelId);
    onModelChange?.(modelId);
  };

  return (
    <div className={cn("w-full", className)}>
      <div className="relative w-full border border-black/10 dark:border-white/10 rounded-xl shadow-sm">
        <div className="relative flex flex-col">
          {isRecording ? (
            <AudioWaveform 
              isRecording={isRecording}
              isPaused={isProcessingAudio}
              className="w-full h-[64px]"
            />
          ) : (
            <div
              className="overflow-y-auto"
              style={{ maxHeight: `${maxHeight}px` }}
            >
              <Textarea
                id={id}
                value={value}
                placeholder={placeholder}
                className="w-full rounded-xl rounded-b-none px-4 py-3 bg-black/5 dark:bg-white/5 border-none dark:text-white placeholder:text-black/70 dark:placeholder:text-white/70 placeholder:text-sm resize-none focus-visible:ring-0 leading-[1.2]"
                ref={textareaRef}
                onKeyDown={handleKeyDown}
                onChange={handleInputChange}
              />
            </div>
          )}

          <div className="h-12 bg-black/5 dark:bg-white/5 rounded-b-xl">
            <div className="flex justify-between items-center h-full px-3">
              <div className="flex items-center gap-3 ml-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="relative h-8 w-8 flex items-center justify-center"
                  onClick={() => document.getElementById('file-input')?.click()}
                >
                  <Paperclip className="w-4 h-4" />
                  <input 
                    id="file-input"
                    type="file" 
                    className="hidden" 
                    onChange={handleFileChange}
                  />
                </Button>

                <div className="h-5 w-px bg-black/10 dark:bg-white/10" />

                <ModelSelector 
                  selectedModelId={selectedModelId}
                  onModelSelect={handleModelSelect}
                  availableModels={availableModels}
                />
              </div>

              <div className="flex items-center gap-3 mr-1">
                <Button
                  onClick={isRecording ? stopRecording : startRecording}
                  variant="ghost"
                  size="icon"
                  disabled={isProcessingAudio}
                  className={cn(
                    "h-8 w-8 flex items-center justify-center",
                    isRecording && "bg-red-500/15 text-red-500 hover:text-red-500 hover:bg-red-500/20",
                    isProcessingAudio && "opacity-50 cursor-not-allowed"
                  )}
                >
                  {isProcessingAudio ? (
                    <div className="w-4 h-4 animate-spin rounded-full border-2 border-gray-400 border-t-transparent" />
                  ) : isRecording ? (
                    <Square className="w-4 h-4" />
                  ) : (
                    <Mic className="w-4 h-4" />
                  )}
                </Button>

                {isLoading ? (
                  <Button
                    onClick={onStop}
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 flex items-center justify-center"
                  >
                    <Square className="w-4 h-4" />
                  </Button>
                ) : (
                  <Button
                    size="icon"
                    variant="outline"
                    disabled={isRecording}
                    onClick={handleSubmit}
                    className={cn(
                      "h-8 w-8 rounded-full transition-all duration-200 ease-in-out border-0 relative overflow-hidden flex items-center justify-center",
                      value.trim() 
                        ? "bg-transparent text-white dark:text-black" 
                        : "border-0 hover:bg-black/5 dark:hover:bg-white/5 scale-100"
                    )}
                  >
                    <AnimatePresence>
                      {value.trim() && (
                        <motion.div
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          exit={{ scale: 0, opacity: 0 }}
                          transition={{ duration: 0.2, ease: "easeOut" }}
                          className="absolute inset-0 rounded-full bg-black dark:bg-white"
                          style={{ originX: 0.5, originY: 0.5 }}
                        />
                      )}
                    </AnimatePresence>
                    <ArrowUp className="w-4 h-4 relative z-10" />
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

AIInputWithSearch.displayName = "AIInputWithSearch";