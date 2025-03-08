import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Trash2, RefreshCw, AlertCircle } from "lucide-react";
import { getUserMemoryChunks, deleteUserMemoryChunk } from "../../api/api.integrations";
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
  memory: string; // Текст из колонки memory
  created_at: string;
}

interface VeyraxConfigProps {
  onUpdate?: () => void;
  disabled?: boolean;
}

export function VeyraxConfig({ onUpdate, disabled = false }: VeyraxConfigProps) {
  const [memoryChunks, setMemoryChunks] = useState<MemoryChunk[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<Record<string, boolean>>({});

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
    } catch (err) {
      console.error("Failed to delete memory chunk:", err);
      setError("Failed to delete memory chunk. Please try again.");
    } finally {
      setIsDeleting(prev => ({ ...prev, [chunkId]: false }));
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4 flex items-center gap-2" role="alert">
          <AlertCircle className="h-4 w-4" />
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {memoryChunks.length === 0 ? (
        <div className="text-center py-6 text-muted-foreground">
          {isLoading ? "Loading memory data..." : "No memory data found."}
        </div>
      ) : (
        <div className="border rounded-md overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-left">Memory</TableHead>
                <TableHead className="text-right"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {memoryChunks.map((chunk) => (
                <TableRow key={chunk.id}>
                  <TableCell className="align-top">
                    <div className="max-h-20 overflow-y-auto">
                      {chunk.memory}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleDeleteChunk(chunk.id);
                      }}
                      disabled={isDeleting[chunk.id] || disabled}
                      className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      {isDeleting[chunk.id] ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}