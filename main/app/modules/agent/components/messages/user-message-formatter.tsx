import React from "react";

interface UserMessageFormatterProps {
  content: string;
}

// Function to format URLs for better display
const formatUserUrl = (url: string): string => {
  try {
    const parsedUrl = new URL(url);
    const domain = parsedUrl.hostname;
    
    // For simplicity, just show the domain and a short part of the path
    return domain + (parsedUrl.pathname !== '/' ? '/...' : '') + (parsedUrl.search ? '?...' : '');
  } catch (e) {
    // If URL parsing fails, fall back to simple truncation
    return url.length > 30 ? url.substring(0, 20) + '...' : url;
  }
};

export function UserMessageFormatter({ content }: UserMessageFormatterProps) {
  // Simple URL regex pattern
  const urlPattern = /(https?:\/\/[^\s]+)/g;
  
  // Replace URLs in the content with formatted versions
  const formattedContent = content.replace(urlPattern, (match) => {
    const formattedUrl = formatUserUrl(match);
    return formattedUrl;
  });
  
  return (
    <div className="whitespace-pre-wrap break-words overflow-hidden text-ellipsis max-w-full">
      {formattedContent}
    </div>
  );
}