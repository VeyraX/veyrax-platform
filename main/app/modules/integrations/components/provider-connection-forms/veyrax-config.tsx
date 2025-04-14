import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Trash2, RefreshCw, AlertCircle, Edit, Plus, Check, X, MoreHorizontal, Eye, EyeOff } from "lucide-react";
import { 
  getUserMemoryChunks, 
  deleteUserMemoryChunk, 
  addUserMemoryChunk,
  updateUserMemoryChunk 
} from "../../api/api.integrations";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

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

// Utility function to truncate text
const truncateText = (text: string, maxLength: number) => {
  if (text.length <= maxLength) {
    return text;
  }
  return text.slice(0, maxLength) + "...";
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
      chunks.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
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
  };

  const handleSaveEdit = async (chunkId: string) => {
    const newValue = editValues[chunkId];
    const newToolValue = editToolValues[chunkId];

    if (newValue === undefined || newValue.trim() === "") return;

    setIsSubmitting(true);
    try {
      const updatedChunk = await updateUserMemoryChunk(chunkId, newValue, newToolValue);
      setMemoryChunks(prev =>
        prev.map(chunk => chunk.id === chunkId ? updatedChunk : chunk)
      );
      if (onUpdate) onUpdate();
      setIsEditing(prev => ({ ...prev, [chunkId]: false }));
    } catch (err) {
      console.error("Failed to update memory chunk:", err);
      setError("Failed to update memory chunk. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddMemory = async () => {
    if (!newMemory || newMemory.trim() === "") return;

    setIsSubmitting(true);
    try {
      const addedChunk = await addUserMemoryChunk(newMemory, newTool);
      setMemoryChunks(prev => [addedChunk, ...prev]);
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

  // Function to toggle expansion state
  const toggleExpandChunk = (chunkId: string) => {
    setExpandedChunks(prev => ({ ...prev, [chunkId]: !prev[chunkId] }));
  };

  const MAX_LENGTH = 150; // Define max length for truncation

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4 flex items-center gap-2" role="alert">
          <AlertCircle className="h-4 w-4" />
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <div className="flex justify-between items-center">
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
        <div className="border p-4 rounded-md">
          <div className="mb-3">
            <Textarea
              value={newMemory}
              onChange={(e) => setNewMemory(e.target.value)}
              placeholder="Enter new memory content..."
              className="mb-3"
              rows={3}
              disabled={isSubmitting}
            />
            <div className="flex items-center gap-2">
              <label htmlFor="new-tool" className="text-sm text-muted-foreground">Tool:</label>
              <Input
                id="new-tool"
                type="text"
                value={newTool}
                onChange={(e) => setNewTool(e.target.value)}
                placeholder="General"
                className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 max-w-[200px]"
                disabled={isSubmitting}
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

      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[60%]">Memory</TableHead>
              <TableHead className="w-[30%]">Tool</TableHead>
              <TableHead className="text-right w-[10%]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={3} className="h-24 text-center">
                  Loading memory data...
                </TableCell>
              </TableRow>
            ) : memoryChunks.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3} className="h-24 text-center">
                  No memory data found.
                </TableCell>
              </TableRow>
            ) : (
              memoryChunks.map((chunk) => (
                <TableRow key={chunk.id} className={isEditing[chunk.id] ? "bg-muted/50" : ""}>
                  {isEditing[chunk.id] ? (
                    <>
                      <TableCell className="py-2">
                        <Textarea
                          value={editValues[chunk.id]}
                          onChange={(e) => setEditValues(prev => ({ ...prev, [chunk.id]: e.target.value }))}
                          className="w-full min-h-[60px]"
                          rows={3}
                          disabled={isSubmitting}
                        />
                      </TableCell>
                      <TableCell className="py-2">
                        <Input
                          type="text"
                          value={editToolValues[chunk.id] || ""}
                          onChange={(e) => setEditToolValues(prev => ({ ...prev, [chunk.id]: e.target.value }))}
                          placeholder="General"
                          className="h-9"
                          disabled={isSubmitting}
                        />
                      </TableCell>
                      <TableCell className="text-right py-2">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleSaveEdit(chunk.id)}
                            disabled={!editValues[chunk.id]?.trim() || isSubmitting}
                            className="h-8 px-2"
                          >
                            {isSubmitting ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleCancelEdit(chunk.id)}
                            disabled={isSubmitting}
                            className="h-8 px-2"
                          >
                            <X className="h-4 w-4"/>
                          </Button>
                        </div>
                      </TableCell>
                    </>
                  ) : (
                    <>
                      <TableCell className="whitespace-pre-wrap break-words">
                        {expandedChunks[chunk.id] 
                          ? (
                            <>
                              {chunk.memory}
                              <button 
                                onClick={() => toggleExpandChunk(chunk.id)} 
                                className="ml-1 text-gray-500 text-xs hover:underline"
                              >
                                Show less
                              </button>
                            </>
                          ) 
                          : chunk.memory.length > MAX_LENGTH 
                            ? (
                              <>
                                {truncateText(chunk.memory, MAX_LENGTH)}
                                <button 
                                  onClick={() => toggleExpandChunk(chunk.id)} 
                                  className="ml-1 text-gray-500 text-xs hover:underline"
                                >
                                  Show more
                                </button>
                              </>
                            )
                            : chunk.memory
                        }
                      </TableCell>
                      <TableCell>{chunk.tool || "General"}</TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu modal={false}>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem
                              onClick={() => handleEditChunk(chunk.id, chunk.memory, chunk.tool)}
                              disabled={disabled || isEditing[chunk.id]}
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
                      </TableCell>
                    </>
                  )}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}