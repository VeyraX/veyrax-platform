"use client";

import { AIInputWithSearch } from "@/app/modules/agent/components/input/ai-input";
import { ChatMessages } from "@/app/modules/agent/components/messages/chat-messages";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FlowChatEmptyState } from "./flow-chat-test-empty-state";
import { type Message } from 'ai/react';

interface FlowChatPanelProps {
  messages: Message[];
  isLoading: boolean;
  chatId: string;
  onSubmit: (message: string) => Promise<void>;
  onStop: () => void;
}

export function FlowChatPanel({ 
  messages, 
  isLoading, 
  chatId, 
  onSubmit, 
  onStop 
}: FlowChatPanelProps) {
  const hasMessages = messages.length > 0;

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      <div className="w-full max-w-3xl flex flex-col h-full mx-auto">
        <ScrollArea className="flex-1 relative">
          {hasMessages ? (
            <div className="pb-[120px]">
              <ChatMessages
                messages={messages}
                isLoading={isLoading}
                chatId={chatId}
                isFlow={true}
              />
            </div>
          ) : (
            <div className="h-full">
              <FlowChatEmptyState />
            </div>
          )}
        </ScrollArea>

        <div className="sticky bottom-0 bg-background py-6">
          <div className="px-4">
            <AIInputWithSearch
              onSubmit={onSubmit}
              isLoading={isLoading}
              onStop={onStop}
              userTools={{}}
              className="max-w-none"
              placeholder="What do you want to know?"
            />
          </div>
        </div>
      </div>
    </div>
  );
}