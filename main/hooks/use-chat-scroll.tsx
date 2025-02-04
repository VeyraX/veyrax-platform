import { useEffect, useRef } from 'react';

export function useChatScroll<T>(
  messages: T[],
  isLoading: boolean,
  options = { threshold: 150, behavior: 'smooth' as ScrollBehavior }
) {
  const containerRef = useRef<HTMLDivElement>(null);
  const lastMessageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const lastMessage = lastMessageRef.current;

    if (!container || !lastMessage) return;

    const shouldAutoScroll = () => {
      const containerHeight = container.clientHeight;
      const scrollTop = container.scrollTop;
      const scrollHeight = container.scrollHeight;
      const distanceFromBottom = scrollHeight - (scrollTop + containerHeight);
      
      return distanceFromBottom <= options.threshold;
    };

    if (shouldAutoScroll()) {
      lastMessage.scrollIntoView({ behavior: options.behavior });
    }
  }, [messages, isLoading, options.threshold, options.behavior]);

  return { containerRef, lastMessageRef };
}