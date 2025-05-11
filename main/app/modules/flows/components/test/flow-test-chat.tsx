"use client";

import { AIInputWithSearch } from "@/app/modules/agent/components/input/ai-input";
import { ChatMessages } from "@/app/modules/agent/components/messages/chat-messages";
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
      <div className="w-full max-w-4xl flex flex-col h-full mx-auto">
        <div className="flex-1 relative overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
          {hasMessages ? (
            <div className="pb-[120px]">
              <ChatMessages
                messages={messages}
                isLoading={isLoading}
                chatId={chatId}
                isFlow={true}
                hideRatings={true}
              />
            </div>
          ) : (
            <div className="h-full">
              <FlowChatEmptyState />
            </div>
          )}
        </div>

        <div className="sticky bottom-0 bg-background py-6">
          <div className="px-4">
            <AIInputWithSearch
              onSubmit={onSubmit}
              isLoading={isLoading}
              onStop={onStop}
              userTools={{}}
              className="max-w-none"
              placeholder="How can I help you with testing?"
              showModelSelector={false}
            />
          </div>
        </div>
      </div>
    </div>
  );
}