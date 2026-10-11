export function parseDOMFromHTML(html: string): Document {
    const parser = new DOMParser();
    return parser.parseFromString(html, 'text/html');
  }
  
  export function extractTextFromHTML(html: string): string {
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    return tempDiv.textContent || '';
  }
  
  export function getActionElementsFromHTML(html: string): NodeListOf<Element> {
    const doc = parseDOMFromHTML(html);
    return doc.querySelectorAll('.action-item');
  }
  
  export function getProviderInfoFromActionElements(actionElements: NodeListOf<Element>): {
    providerName: string;
    actionSlug: string;
  }[] {
    const result: { providerName: string; actionSlug: string; }[] = [];
    
    actionElements.forEach(item => {
      const providerName = item.getAttribute('data-provider');
      const actionSlug = item.getAttribute('data-action');
      
      if (providerName && actionSlug) {
        result.push({ providerName, actionSlug });
      }
    });
    
    return result;
  }

  // Check whether HTML content is effectively empty
  export function isEmptyHTML(html: string): boolean {
    // Empty string is empty
    if (!html || html.trim() === '') return true;
    
    // Check for visible text
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    const hasText = (tempDiv.textContent?.trim().length ?? 0) > 0;
    
    // No text: check the most common "empty" content patterns
    const emptyPatterns = [
      '<p><br></p>',
      '<p></p>',
      '<br>',
      '<div></div>',
      '<div><br></div>'
    ];
    
    return !hasText || emptyPatterns.includes(html.trim());
  }