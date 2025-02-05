import { Tree, File, Folder, type TreeViewElement } from "@/components/ui/tree-view"

interface FileTreeProps {
  code: Array<{ path: string, snippet: string }>
  onFileSelect: (id: string) => void
}

export function FileTree({ code, onFileSelect }: FileTreeProps) {
  const buildFileTree = (codeItems: Array<{ path: string, snippet: string }>): TreeViewElement[] => {
    const tree: TreeViewElement[] = []
    
    codeItems.forEach((item, index) => {
      const parts = item.path.split('/')
      let currentLevel = tree
      
      parts.forEach((part, i) => {
        const isLastPart = i === parts.length - 1
        const existing = currentLevel.find(node => node.name === part)
        
        if (existing) {
          if (!isLastPart) {
            currentLevel = existing.children || []
          }
        } else {
          const newNode: TreeViewElement = {
            id: isLastPart ? `file-${index}` : `folder-${part}-${index}`,
            name: part,
            children: isLastPart ? undefined : [],
            isSelectable: isLastPart
          }
          currentLevel.push(newNode)
          if (!isLastPart) {
            currentLevel = newNode.children!
          }
        }
      })
    })
    
    return tree
  }

  const renderTreeItems = (items: TreeViewElement[]) => {
    return items.map((item) => {
      if (item.children) {
        return (
          <Folder key={item.id} value={item.id} element={item.name}>
            {renderTreeItems(item.children)}
          </Folder>
        )
      }
      
      return (
        <File 
          key={item.id} 
          value={item.id}
          handleSelect={onFileSelect}
        >
          {item.name}
        </File>
      )
    })
  }

  const getAllFolderIds = (nodes: TreeViewElement[]): string[] => {
    return nodes.reduce((acc: string[], node) => {
      if (node.id.startsWith('folder-')) {
        acc.push(node.id)
        if (node.children) {
          acc.push(...getAllFolderIds(node.children))
        }
      }
      return acc
    }, [])
  }

  const treeElements = buildFileTree(code)

  return (
    <div className="w-1/3">
      <Tree 
        elements={treeElements}
        initialSelectedId="file-0"
        initialExpandedItems={getAllFolderIds(treeElements)}
      >
        {renderTreeItems(treeElements)}
      </Tree>
    </div>
  )
}