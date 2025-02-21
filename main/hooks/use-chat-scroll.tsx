import { useRef, useEffect, useState } from 'react';

interface UseAutoScrollProps {
  messagesEndRef: React.RefObject<HTMLDivElement>;
  isLoading: boolean;
  messages: any[];
}

export function useAutoScroll({ messagesEndRef, isLoading, messages }: UseAutoScrollProps) {
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const prevScrollTop = useRef<number | null>(null);
  const SCROLL_THRESHOLD = 50;
  const isManualScroll = useRef(false);
  const lastMessageContentRef = useRef<string>('');

  const scrollToBottom = () => {
    if (!shouldAutoScroll || isManualScroll.current) return;
    
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ 
        behavior: "smooth",
        block: "end"
      });
    }, 100);
  };

  useEffect(() => {
    const messageContainer = messagesEndRef.current?.parentElement;
    if (!messageContainer) return;

    function onScroll() {
      const currentScrollTop = messageContainer!.scrollTop;
      
      if (Math.abs(currentScrollTop - (prevScrollTop.current ?? 0)) > 1) {
        isManualScroll.current = true;
        setTimeout(() => {
          isManualScroll.current = false;
        }, 5000);
      }

      if (currentScrollTop < (prevScrollTop.current ?? 0) - 1) {
        setShouldAutoScroll(false);
      } else if (
        messageContainer!.scrollHeight - messageContainer!.clientHeight <= currentScrollTop + SCROLL_THRESHOLD
      ) {
        setShouldAutoScroll(true);
      }
      
      prevScrollTop.current = currentScrollTop;
    }

    messageContainer.addEventListener('scroll', onScroll);
    return () => messageContainer.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      const currentContent = JSON.stringify(lastMessage);

      if (currentContent !== lastMessageContentRef.current && shouldAutoScroll) {
        lastMessageContentRef.current = currentContent;
        scrollToBottom();
      }
    }
  }, [messages, shouldAutoScroll]);

  useEffect(() => {
    if (!isLoading) {
      scrollToBottom();
    }
  }, [isLoading, shouldAutoScroll]);

  return { shouldAutoScroll };
}