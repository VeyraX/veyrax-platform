import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Trash2, RefreshCw, AlertCircle, Edit, Plus, Save, X, MoreHorizontal } from "lucide-react";
import { 
  getUserMemoryChunks, 
  deleteUserMemoryChunk, 
  addUserMemoryChunk,
  updateUserMemoryChunk 
} from "../../api/api.integrations";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface MemoryChunk {
  id: string;
  memory: string;
  created_at: string;
  tool?: string;
}

interface VeyraxConfigProps {
  onUpdate?: () => void;
  disabled?: boolean;
}

const truncateText = (text: string, maxLength: number = 90): string => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  
  return text.substring(0, maxLength) + '...';
};

export function VeyraxConfig({ onUpdate, disabled = false }: VeyraxConfigProps) {
  const [memoryChunks, setMemoryChunks] = useState<MemoryChunk[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<Record<string, boolean>>({});
  const [isEditing, setIsEditing] = useState<Record<string, boolean>>({});
  const [editValues, setEditValues] = useState<Record<string, string>>({});
  const [editToolValues, setEditToolValues] = useState<Record<string, string>>({});
  const [newMemory, setNewMemory] = useState("");
  const [newTool, setNewTool] = useState("");
  const [isAddingMemory, setIsAddingMemory] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [expandedChunks, setExpandedChunks] = useState<Record<string, boolean>>({});

  const fetchMemoryChunks = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const chunks = await getUserMemoryChunks();
      setMemoryChunks(chunks);
    } catch (err) {
      console.error("Failed to fetch memory chunks:", err);
      setError("Failed to load memory data. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMemoryChunks();
  }, []);

  const handleDeleteChunk = async (chunkId: string) => {
    setIsDeleting(prev => ({ ...prev, [chunkId]: true }));
    try {
      await deleteUserMemoryChunk(chunkId);
      setMemoryChunks(prev => prev.filter(chunk => chunk.id !== chunkId));
      if (onUpdate) onUpdate();
    } catch (err) {
      console.error("Failed to delete memory chunk:", err);
      setError("Failed to delete memory chunk. Please try again.");
    } finally {
      setIsDeleting(prev => ({ ...prev, [chunkId]: false }));
    }
  };

  const handleEditChunk = (chunkId: string, memory: string, tool?: string) => {
    setIsEditing(prev => ({ ...prev, [chunkId]: true }));
    setEditValues(prev => ({ ...prev, [chunkId]: memory }));
    setEditToolValues(prev => ({ ...prev, [chunkId]: tool || "" }));
  };

  const handleCancelEdit = (chunkId: string) => {
    setIsEditing(prev => ({ ...prev, [chunkId]: false }));
    setEditValues(prev => ({ ...prev, [chunkId]: "" }));
    setEditToolValues(prev => ({ ...prev, [chunkId]: "" }));
  };

  const handleSaveEdit = async (chunkId: string) => {
    const newValue = editValues[chunkId];
    const newTool = editToolValues[chunkId];
    
    if (!newValue || newValue.trim() === "") return;

    setIsEditing(prev => ({ ...prev, [chunkId]: false }));
    try {
      const updatedChunk = await updateUserMemoryChunk(chunkId, newValue, newTool);
      setMemoryChunks(prev => 
        prev.map(chunk => chunk.id === chunkId ? updatedChunk : chunk)
      );
      if (onUpdate) onUpdate();
    } catch (err) {
      console.error("Failed to update memory chunk:", err);
      setError("Failed to update memory chunk. Please try again.");
    }
  };

  const handleAddMemory = async () => {
    if (!newMemory || newMemory.trim() === "") return;
    
    setIsSubmitting(true);
    try {
      const addedChunk = await addUserMemoryChunk(newMemory, newTool);
      setMemoryChunks(prev => [...prev, addedChunk]);
      setNewMemory("");
      setNewTool("");
      setIsAddingMemory(false);
      if (onUpdate) onUpdate();
    } catch (err) {
      console.error("Failed to add memory chunk:", err);
      setError("Failed to add memory chunk. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleExpandChunk = (chunkId: string) => {
    setExpandedChunks(prev => ({ ...prev, [chunkId]: !prev[chunkId] }));
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4 flex items-center gap-2" role="alert">
          <AlertCircle className="h-4 w-4" />
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Memory Chunks</h3>
        <Button 
          onClick={() => setIsAddingMemory(true)} 
          disabled={isAddingMemory || disabled}
          size="sm"
          className="flex items-center gap-1"
        >
          <Plus className="h-4 w-4" /> Add Memory
        </Button>
      </div>

      {isAddingMemory && (
        <div className="border p-4 rounded-md mb-4">
          <div className="mb-3">
            <Textarea
              value={newMemory}
              onChange={(e) => setNewMemory(e.target.value)}
              placeholder="Enter new memory content..."
              className="mb-3"
              rows={3}
            />
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Tool:</span>
              <input
                type="text"
                value={newTool}
                onChange={(e) => setNewTool(e.target.value)}
                placeholder="General"
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 max-w-[200px]"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setIsAddingMemory(false);
                setNewMemory("");
                setNewTool("");
              }}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={handleAddMemory}
              disabled={!newMemory.trim() || isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Memory"
              )}
            </Button>
          </div>
        </div>
      )}

      {memoryChunks.length === 0 ? (
        <div className="text-center py-6 text-muted-foreground">
          {isLoading ? "Loading memory data..." : "No memory data found."}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {memoryChunks.map((chunk) => (
            <Card key={chunk.id} className="group relative border shadow-none">
              {isEditing[chunk.id] ? (
                <CardContent className="p-4">
                  <Textarea
                    value={editValues[chunk.id]}
                    onChange={(e) => setEditValues(prev => ({ ...prev, [chunk.id]: e.target.value }))}
                    className="w-full mb-3"
                    rows={4}
                  />
                  
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-sm text-muted-foreground">Tool:</span>
                    <input
                      type="text"
                      value={editToolValues[chunk.id] || ""}
                      onChange={(e) => setEditToolValues(prev => ({ ...prev, [chunk.id]: e.target.value }))}
                      placeholder="General"
                      className="flex h-8 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 max-w-[200px]"
                    />
                  </div>
                  
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleCancelEdit(chunk.id)}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleSaveEdit(chunk.id)}
                      disabled={!editValues[chunk.id]?.trim()}
                    >
                      Save
                    </Button>
                  </div>
                </CardContent>
              ) : (
                <>
                  <CardContent className="p-4">
                    <div 
                      className="h-[100px] overflow-y-auto pr-1 whitespace-normal break-words cursor-pointer" 
                      style={{ overflowY: 'auto', WebkitOverflowScrolling: 'touch' }}
                      onClick={() => toggleExpandChunk(chunk.id)}
                    >
                      {chunk.memory.length > 90 && !expandedChunks[chunk.id] ? (
                        <>
                          {truncateText(chunk.memory)}
                          <span className="text-muted-foreground text-sm ml-1">show more</span>
                        </>
                      ) : (
                        chunk.memory
                      )}
                    </div>
                  </CardContent>
                  <Separator />
                  <CardFooter className="flex justify-between items-center p-2 bg-muted/20">
                    <div className="text-sm font-medium">
                      {chunk.tool || "General"}
                    </div>
                    <DropdownMenu modal={false}>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8 p-0">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem 
                          onClick={() => handleEditChunk(chunk.id, chunk.memory, chunk.tool)}
                          disabled={disabled}
                          className="cursor-pointer"
                        >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                          onClick={() => handleDeleteChunk(chunk.id)}
                          disabled={isDeleting[chunk.id] || disabled}
                          className="cursor-pointer text-destructive focus:text-destructive"
                        >
                          {isDeleting[chunk.id] ? (
                            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                          ) : (
                            <Trash2 className="h-4 w-4 mr-2" />
                          )}
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </CardFooter>
                </>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}