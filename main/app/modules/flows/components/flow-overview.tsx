import { isEmptyHTML } from "./flow-description-html";
import { ToolsList } from "./flow-description-tool-detector";
import { useEffect, useRef } from "react";
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-tsx';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-json';
import 'prismjs/plugins/line-numbers/prism-line-numbers';
import 'prismjs/plugins/line-numbers/prism-line-numbers.css';

interface FlowOverviewProps {
  description: string;
  tools: any[];
}

export function FlowOverview({ description, tools }: FlowOverviewProps) {
  const contentRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (contentRef.current && description) {
      contentRef.current.innerHTML = cleanHtml(description);
      Prism.highlightAllUnder(contentRef.current);
      
      contentRef.current.querySelectorAll('pre').forEach(pre => {
        pre.style.maxHeight = '300px';
        pre.style.overflow = 'auto';
        pre.style.borderRadius = '0.375rem';
        pre.classList.add('line-numbers');
      });
    }
  }, [description]);

  const cleanHtml = (html: string): string => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
  
    doc.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
      heading.classList.add('font-semibold', 'mb-2', 'mt-4');
      
      if (heading.tagName.toLowerCase() === 'h3') {
        heading.classList.add('text-lg');
      }
    });
    
    doc.querySelectorAll('ol').forEach(list => {
      list.classList.add('list-decimal', 'pl-5', 'my-3');
    });
    
    doc.querySelectorAll('ul').forEach(list => {
      list.classList.add('list-disc', 'pl-5', 'my-3');
    });
    
    doc.querySelectorAll('li').forEach(item => {
      item.classList.add('ml-2', 'my-3');
    });
    
    doc.querySelectorAll('pre').forEach(preElement => {
      preElement.classList.add('line-numbers');
      
      const codeElement = preElement.querySelector('code');
      if (codeElement) {
        const languageClass = Array.from(codeElement.classList)
          .find(cls => cls.startsWith('language-'));
        
        if (!languageClass) {
          codeElement.classList.add('language-javascript');
        }
      } else {
        const content = preElement.innerHTML;
        preElement.innerHTML = `<code class="language-javascript">${content}</code>`;
      }
    });
    
    return doc.body.innerHTML;
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-md border p-6 space-y-4">
        <h2 className="text-xl font-medium text-foreground">Overview</h2>
        
        {description && !isEmptyHTML(description) ? (
          <div className="prose prose-sm md:prose-base max-w-none text-foreground prose-headings:font-semibold prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-p:text-foreground/90 prose-ul:list-disc prose-ol:list-decimal prose-ul:pl-5 prose-ol:pl-5 prose-li:my-3">
            <div ref={contentRef} />
          </div>
        ) : (
          <div className="text-muted-foreground">
            No description available for this flow.
          </div>
        )}
      </div>
      
      <div className="bg-white rounded-md border p-6 space-y-4">
        <h2 className="text-xl font-medium text-foreground">Tools</h2>
        <div>
          <ToolsList tools={tools} />
        </div>
      </div>
    </div>
  );
} 