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
    actionName: string;
  }[] {
    const result: { providerName: string; actionName: string; }[] = [];
    
    actionElements.forEach(item => {
      const providerName = item.getAttribute('data-provider');
      const actionName = item.getAttribute('data-action');
      
      if (providerName && actionName) {
        result.push({ providerName, actionName });
      }
    });
    
    return result;
  }

  // Новая функция для проверки фактической пустоты HTML содержимого
  export function isEmptyHTML(html: string): boolean {
    // Пустая строка - очевидно пусто
    if (!html || html.trim() === '') return true;
    
    // Проверяем, есть ли видимый текст
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    const hasText = (tempDiv.textContent?.trim().length ?? 0) > 0;
    
    // Если текста нет, проверяем на самые частые паттерны "пустого" контента
    const emptyPatterns = [
      '<p><br></p>',
      '<p></p>',
      '<br>',
      '<div></div>',
      '<div><br></div>'
    ];
    
    return !hasText || emptyPatterns.includes(html.trim());
  }