import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { FlowRunParts } from "./flow-run-parts";
import { UserFlowRun } from "../../api/types.flows";

interface ScheduleSheetProps {
  isOpen: boolean;
  onClose: () => void;
  flowRun: UserFlowRun;
}

export function ScheduleSheet({ isOpen, onClose, flowRun }: ScheduleSheetProps) {
  const parts = flowRun?.payload?.parts.map(part => ({
    ...part,
    toolInvocation: part.toolInvocation ? {
      ...part.toolInvocation,
      metadata: flowRun.payload?.metadata
    } : undefined
  })) || [];

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent className="sm:max-w-4xl w-[95%] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Flow Run Details</SheetTitle>
        </SheetHeader>
        <div className="mt-6 pb-8">
          {parts && parts.length > 0 ? (
            <FlowRunParts parts={parts} />
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Payload will appear soon... Flow is running.</p>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
