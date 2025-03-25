import { useState, useRef, useEffect } from "react";
import { ProviderAction } from "@/app/modules/flows/api/types.flows";

interface CursorPosition {
  top: number;
  left: number;
}

export function useActionsMention(contentEditableRef: React.RefObject<any>, providedActions: any[] = []) {
  const [actions, setActions] = useState<any[]>(providedActions);
  const [filteredActions, setFilteredActions] = useState<any[]>(providedActions);
  const [showActions, setShowActions] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [cursorPosition, setCursorPosition] = useState<CursorPosition | null>(null);
  const [selectedActionIndex, setSelectedActionIndex] = useState(0);
  const actionsListRef = useRef<HTMLDivElement>(null);
  const actionJustSelected = useRef(false);
  const actionJustSelectedTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    setActions(providedActions);
    setFilteredActions(providedActions);
  }, [providedActions]);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredActions(actions);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = actions.filter(action => 
      action.action_slug.toLowerCase().includes(query) || 
      action.provider_name?.toLowerCase().includes(query)
    );
    
    setFilteredActions(filtered);
  }, [searchQuery, actions]);

  useEffect(() => {
    setSelectedActionIndex(0);
  }, [filteredActions]);

  useEffect(() => {
    if (actionsListRef.current && filteredActions.length > 0) {
      const selectedItem = actionsListRef.current.querySelector(`[data-index="${selectedActionIndex}"]`);
      if (selectedItem) {
        selectedItem.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [selectedActionIndex]);

  useEffect(() => {
    if (!showActions) return;

    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (actionJustSelected.current) return;
      
      if (!showActions || filteredActions.length === 0) return;
      
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedActionIndex(prev => 
            prev < filteredActions.length - 1 ? prev + 1 : prev
          );
          break;
          
        case 'ArrowUp':
          e.preventDefault();
          setSelectedActionIndex(prev => prev > 0 ? prev - 1 : 0);
          break;
          
        case 'Enter':
          if (filteredActions.length > 0) {
            e.preventDefault();
            handleActionSelect(filteredActions[selectedActionIndex]);
          }
          break;
          
        case 'Escape':
          e.preventDefault();
          setShowActions(false);
          setSearchQuery("");
          setCursorPosition(null);
          break;
      }
    };

    document.addEventListener('keydown', handleGlobalKeyDown as any, true);
    
    return () => {
      document.removeEventListener('keydown', handleGlobalKeyDown as any, true);
    };
  }, [showActions, filteredActions, selectedActionIndex]);

  const getCursorPosition = () => {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return null;
    
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    
    const editorRect = contentEditableRef.current?.el?.getBoundingClientRect() || 
                      contentEditableRef.current?.getBoundingClientRect();
    
    if (!editorRect) return null;
    
    return {
      top: Math.min(rect.bottom - editorRect.top + 5, editorRect.height - 50),
      left: Math.max(0, rect.left - editorRect.left)
    };
  };

  const handleActionSelect = (action: any) => {
    actionJustSelected.current = true;
    
    if (actionJustSelectedTimer.current) {
      clearTimeout(actionJustSelectedTimer.current);
    }
    
    actionJustSelectedTimer.current = setTimeout(() => {
      actionJustSelected.current = false;
    }, 500);
    
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return;
    
    const range = sel.getRangeAt(0);
    const node = range.startContainer;
    
    if (node.nodeType !== 3) return;
    
    const text = node.textContent || '';
    const offset = range.startOffset;
    
    let atIndex = -1;
    for (let i = offset - 1; i >= 0; i--) {
      if (text[i] === '@') {
        atIndex = i;
        break;
      } else if (/\s/.test(text[i])) {
        break;
      }
    }
    
    if (atIndex === -1) return;
    
    const tempRange = document.createRange();
    tempRange.setStart(node, atIndex);
    tempRange.setEnd(node, offset);
    
    tempRange.deleteContents();
    
    const actionElement = document.createElement('span');
    actionElement.className = 'inline-flex items-center gap-1 bg-white border border-gray-200 rounded-md px-1 py-0.5 mx-0.5 action-item shadow-sm';
    actionElement.contentEditable = 'false';
    
    actionElement.setAttribute('data-provider', action.provider_name || '');
    actionElement.setAttribute('data-action', action.action_slug || '');
    
    const imgContainer = document.createElement('div');
    imgContainer.className = 'h-3.5 w-3.5 rounded-sm overflow-hidden flex items-center justify-center bg-white';
    
    const imgElement = document.createElement('img');
    imgElement.src = action.logo_url;
    imgElement.alt = action.action_slug;
    imgElement.className = 'max-h-full max-w-full object-contain';
    
    imgContainer.appendChild(imgElement);
    
    const textElement = document.createElement('span');
    textElement.className = 'text-primary text-xs font-medium';
    textElement.textContent = action.action_slug;
    
    actionElement.appendChild(imgContainer);
    actionElement.appendChild(textElement);
    
    tempRange.insertNode(actionElement);
    
    const spaceNode = document.createTextNode('\u00A0');
    actionElement.parentNode?.insertBefore(spaceNode, actionElement.nextSibling);
    
    const newRange = document.createRange();
    newRange.setStartAfter(spaceNode);
    newRange.collapse(true);
    
    sel.removeAllRanges();
    sel.addRange(newRange);
    
    if (contentEditableRef.current) {
      const el = contentEditableRef.current.el || contentEditableRef.current;
      if (el && typeof el.innerHTML === 'string') {
        return el.innerHTML;
      }
    }
    
    setShowActions(false);
    setSearchQuery("");
    setCursorPosition(null);
    
    return null;
  };

  const processEditorChange = (html: string, evt: any) => {
    if (actionJustSelected.current) {
      return {
        showActions: false,
        searchQuery: "",
        cursorPosition: null
      };
    }
    
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) {
      return {
        showActions: false,
        searchQuery: "",
        cursorPosition: null
      };
    }
    
    const range = sel.getRangeAt(0);
    const node = range.startContainer;
    const offset = range.startOffset;
    
    let parent = node.parentNode;
    while (parent && parent !== contentEditableRef.current?.el) {
      if (parent.nodeType === 1 && (parent as HTMLElement).classList.contains('action-item')) {
        return {
          showActions: false,
          searchQuery: "",
          cursorPosition: null
        };
      }
      parent = parent.parentNode;
    }
    
    if (node.nodeType === 3) {
      const text = node.textContent || '';
      let currentPos = offset;
      
      let i = currentPos - 1;
      while (i >= 0) {
        if (text[i] === '@') {
          const query = text.substring(i + 1, currentPos);
          
          const position = getCursorPosition();
          
          return {
            showActions: true,
            searchQuery: query,
            cursorPosition: position
          };
        } else if (/\s/.test(text[i])) {
          break;
        }
        i--;
      }
    }
    
    return {
      showActions: false,
      searchQuery: "",
      cursorPosition: null
    };
  };

  return {
    actions,
    filteredActions,
    showActions,
    setShowActions,
    searchQuery,
    setSearchQuery,
    cursorPosition,
    setCursorPosition,
    selectedActionIndex,
    setSelectedActionIndex,
    actionsListRef,
    handleActionSelect,
    processEditorChange
  };
}