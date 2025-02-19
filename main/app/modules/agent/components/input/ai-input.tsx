"use client";

import { Globe, Paperclip, Send, Mic, Square } from "lucide-react";
import { useState, useRef } from "react";
import { Textarea } from "@/components/ui/textarea";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { useAutoResizeTextarea } from "@/hooks/use-auto-resize-textarea";
import { Button } from "@/components/ui/button";
import { CircleStop } from "lucide-react";
import { AudioWaveform } from "./audio-input"
import { ToolSuggestionsCommand } from "../suggestions/tool-suggestions"

interface AIInputWithSearchProps {
  id?: string;
  placeholder?: string;
  minHeight?: number;
  maxHeight?: number;
  onSubmit?: (value: string) => void;
  onFileSelect?: (file: File) => void;
  onVoiceText?: (text: string) => void;
  className?: string;
  isLoading?: boolean;
  onStop?: () => void;
  onToolSelect?: (tool: { apiName: string, question: string }) => void;
  type?: 'default' | 'generate';
  onAddDocLink?: (link: string) => void;
  onRemoveDocLink?: (link: string) => void;
  onShowSuggestions?: (show: boolean) => void;
  userTools: Record<string, any>;
}

export function AIInputWithSearch({
  id = "ai-input-with-search",
  minHeight = 64,
  maxHeight = 256,
  onSubmit,
  onFileSelect,
  onVoiceText,
  className,
  isLoading,
  onStop,
  onShowSuggestions,
  userTools,
}: AIInputWithSearchProps) {
  const [value, setValue] = useState("");
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight,
    maxHeight,
  });
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [isProcessingAudio, setIsProcessingAudio] = useState(false);
  const [showCommands, setShowCommands] = useState(false);
  const [selectedTool, setSelectedTool] = useState<{ apiName: string, question: string } | null>(null);

  const handleSubmit = () => {
    const trimmedValue = value.trim();
    if (trimmedValue) {
      onSubmit?.(trimmedValue);
      setValue("");
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
        setValue(data.text);
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
    setValue(newValue);
    
    // Show command menu when slash is typed at the start
    if (newValue.startsWith('/')) {
      setShowCommands(true);
      onShowSuggestions?.(false);
    } else {
      setShowCommands(false);
      onShowSuggestions?.(true);
    }
    
    adjustHeight();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (showCommands && ['ArrowUp', 'ArrowDown', 'Enter'].includes(e.key)) {
      e.preventDefault();
      return;
    }
    
    if (e.key === 'Enter' && !e.shiftKey && !showCommands) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleToolSelect = (tool: { apiName: string, question: string }) => {
    setValue(tool.question);
    setShowCommands(false);
    onShowSuggestions?.(true);
    setSelectedTool(tool);
    adjustHeight();
  };

  return (
    <div className={cn("w-full", className)}>
      <div className="relative w-full">
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
                placeholder="Ask anything, press '/' to search actions..."
                className="w-full rounded-xl rounded-b-none px-4 py-3 bg-black/5 dark:bg-white/5 border-none dark:text-white placeholder:text-black/70 dark:placeholder:text-white/70 resize-none focus-visible:ring-0 leading-[1.2]"
                ref={textareaRef}
                onKeyDown={handleKeyDown}
                onChange={handleInputChange}
              />
            </div>
          )}

          {showCommands && (
            <div className="absolute bottom-full mb-1 w-full z-10">
              <ToolSuggestionsCommand 
                onSelect={handleToolSelect}
                isOpen={showCommands}
                searchQuery={value}
                userTools={userTools}
              />
            </div>
          )}

          <div className="h-12 bg-black/5 dark:bg-white/5 rounded-b-xl">
            <div className="absolute left-3 bottom-3 flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                className="relative"
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
            </div>
            <div className="absolute right-3 bottom-3 flex items-center gap-2">
              <Button
                onClick={isRecording ? stopRecording : startRecording}
                variant="ghost"
                size="icon"
                disabled={isProcessingAudio}
                className={cn(
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
                  className="gap-2"
                >
                  <Square className="w-4 h-4" />
                </Button>
              ) : (
                <Button
                  size="icon"
                  variant="outline"
                  disabled={isRecording}
                  onClick={handleSubmit}
                >
                  <Send className="w-4 h-4" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}