import { isEmptyHTML } from "./flow-description-html";
import { ToolsList } from "./flow-description-tool-detector";

interface FlowOverviewProps {
  description: string;
  tools: any[];
}

export function FlowOverview({ description, tools }: FlowOverviewProps) {
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
    
    return doc.body.innerHTML;
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-md border p-6 space-y-4">
        <h2 className="text-xl font-medium text-foreground">Overview</h2>
        
        {description && !isEmptyHTML(description) ? (
          <div className="prose prose-sm md:prose-base max-w-none text-foreground prose-headings:font-semibold prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-p:text-foreground/90 prose-ul:list-disc prose-ol:list-decimal prose-ul:pl-5 prose-ol:pl-5 prose-li:my-3">
            <div dangerouslySetInnerHTML={{ __html: cleanHtml(description) }} />
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