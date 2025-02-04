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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

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
  type: "Generate" | "Preview";
  onTypeChange?: (type: "Generate" | "Preview") => void;
}

export function AIInputWithSearch({
  id = "ai-input-with-search",
  placeholder = "Search the web...",
  minHeight = 64,
  maxHeight = 256,
  onSubmit,
  onFileSelect,
  onVoiceText,
  className,
  isLoading,
  onStop,
  type = "Generate",
  onTypeChange
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

  const getPlaceholder = () => {
    if (type === "Generate" || type === "Preview") {
      return `Please ${type.toLowerCase()}...`;
    }
    return placeholder;
  };

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
                placeholder={getPlaceholder()}
                className="w-full rounded-xl rounded-b-none px-4 py-3 bg-black/5 dark:bg-white/5 border-none dark:text-white placeholder:text-black/70 dark:placeholder:text-white/70 resize-none focus-visible:ring-0 leading-[1.2]"
                ref={textareaRef}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
                onChange={(e) => {
                  setValue(e.target.value);
                  adjustHeight();
                }}
              />
            </div>
          )}

          <div className="h-12 bg-black/5 dark:bg-white/5 rounded-b-xl">
            <div className="absolute left-3 bottom-3 flex items-center gap-2">
              <label className="cursor-pointer rounded-lg p-2 bg-black/5 dark:bg-white/5">
                <input 
                  type="file" 
                  className="hidden" 
                  onChange={handleFileChange}
                />
                <Paperclip className="w-4 h-4 text-black/40 dark:text-white/40 hover:text-black dark:hover:text-white transition-colors" />
              </label>
              <Select 
                value={type} 
                onValueChange={(value: "Generate" | "Preview") => onTypeChange?.(value)}
              >
                <SelectTrigger className="w-[100px] h-8 bg-black/5 dark:bg-white/5 border-none text-sm px-2">
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Generate">Generate</SelectItem>
                  <SelectItem value="Preview">Preview</SelectItem>
                </SelectContent>
              </Select>
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