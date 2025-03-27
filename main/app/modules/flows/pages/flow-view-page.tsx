"use client";

import { useEffect, useState } from "react";
import { getFlowById, getUserActions, getPublicFlowById, getFlowActions, getPublicFlowActions, getActionsByIds } from "../api/api.flows";
import { useRouter } from "next/navigation";
import { FlowHeader } from "../components/header";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { createClient } from '@/lib/utils/supabase/client';
import { ScheduleView } from "../components/schedule/schedule-view";
import { FlowSchedule, UserFlowRun } from "../api/types.flows";
import { getFlowSchedule, getFlowRuns } from "../api/api.schedule.flows";
import { FlowOverview } from "../components/flow-overview";
import { FlowApiDocs } from "../components/flow-api-docs";
import { ScheduleTabContent } from "../components/create/schedule-tab-content";

interface FlowViewPageProps {
  flowId: string;
  isPublic?: boolean;
}

export default function FlowViewPage({ flowId, isPublic = false }: FlowViewPageProps) {
  const router = useRouter();
  const [flow, setFlow] = useState<any>(null);
  const [actions, setActions] = useState<any[]>([]);
  const [isOwner, setIsOwner] = useState(false);
  const [isLoadingFlow, setIsLoadingFlow] = useState(true);
  const [usedTools, setUsedTools] = useState<any[]>([]);
  const [flowActions, setFlowActions] = useState<string[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [schedule, setSchedule] = useState<FlowSchedule | null>(null);
  const [flowRuns, setFlowRuns] = useState<UserFlowRun[]>([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [flowStatus, setFlowStatus] = useState<'Active' | 'Draft'>('Draft');
  
  const loadScheduleAndRuns = async () => {
    if (!flowId) return;
    
    try {
      const [scheduleData, runsData] = await Promise.all([
        getFlowSchedule(flowId),
        getFlowRuns(flowId)
      ]);
      console.log('Loaded schedule and runs:', { schedule: scheduleData, runs: runsData });
      setSchedule(scheduleData);
      setFlowRuns(runsData || []);
    } catch (error) {
      console.error('Error loading schedule and runs:', error);
    }
  };
  
  useEffect(() => {
    const checkAuth = async () => {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      setIsAuthenticated(!!user);
    };
    
    checkAuth();
  }, []);
  
  useEffect(() => {
    const loadFlow = async () => {
      try {
        setIsLoadingFlow(true);
        
        if (isPublic) {
          const publicFlowData = await getPublicFlowById(flowId);
          if (publicFlowData) {
            setFlow(publicFlowData);
            setIsOwner(false);
            
            try {
              const flowActionsData = await getPublicFlowActions(flowId);
              setFlowActions(flowActionsData);
              
              if (flowActionsData.length > 0) {
                const actionsData = await getActionsByIds(flowActionsData);
                setActions(actionsData);
              } else {
                setActions([]);
              }
            } catch (actionsError) {
              console.error('Error loading actions for public flow:', actionsError);
              setFlowActions([]);
              setActions([]);
            }
          } else {
            setFlow(null);
          }
        } else {
          try {
            const flowData = await getFlowById(flowId);
            if (flowData) {
              setFlow(flowData);
              setIsOwner(true);
              
              const actionsData = await getUserActions();
              setActions(actionsData);
              
              const flowActionsData = await getFlowActions(flowId);
              setFlowActions(flowActionsData);
            }
          } catch (error) {
            console.error('Error fetching flow by ID:', error);
            setFlow(null);
          }
        }
      } catch (error) {
        console.error('Error loading flow:', error);
        setFlow(null);
      } finally {
        setIsLoadingFlow(false);
      }
    };
    
    if (flowId) {
      loadFlow();
    }
  }, [flowId, isPublic]);
  
  useEffect(() => {
    if (flow && actions.length > 0 && flowActions.length > 0) {
      const toolsMap = new Map();
      
      const relevantActions = isPublic 
        ? actions 
        : actions.filter(action => flowActions.includes(action.action_id));
      
      relevantActions.forEach(action => {
        if (!toolsMap.has(action.provider_id)) {
          toolsMap.set(action.provider_id, {
            provider_id: action.provider_id,
            provider_name: action.provider_name,
            logo_url: action.logo_url
          });
        }
      });
      
      setUsedTools(Array.from(toolsMap.values()));
    }
  }, [flow, actions, flowActions, isPublic]);
  
  useEffect(() => {
    loadScheduleAndRuns();
  }, [flowId]);
  
  useEffect(() => {
    if (flow?.status) {
      setFlowStatus(flow.status);
    }
  }, [flow]);
  
  const handleBack = () => {
    router.back();
  };
  
  const handleViewDetails = (runId: string) => {
    router.push(`/flows/${flowId}/runs/${runId}`);
  };
  
  if (isLoadingFlow) {
    return (
      <div className="h-screen overflow-hidden flex flex-col">
        <div className="flex items-center justify-between w-full px-4 py-2 bg-white border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Skeleton className="w-6 h-6 rounded-full" />
            <Skeleton className="w-40 h-5" />
          </div>
          <Skeleton className="w-20 h-7 rounded-full" />
        </div>
        
        <div className="flex-1 overflow-hidden p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <div className="bg-white rounded-md border p-6 space-y-4">
                <Skeleton className="w-32 h-6" />
                <Skeleton className="w-full h-40" />
              </div>
              
              <div className="bg-white rounded-md border p-6 space-y-4">
                <Skeleton className="w-24 h-6" />
                <Skeleton className="w-full h-20" />
              </div>
            </div>
            
            <div className="flex flex-col space-y-6">
              <div className="bg-white rounded-md border p-6 space-y-4">
                <Skeleton className="w-32 h-6" />
                <div className="space-y-3">
                  <Skeleton className="w-full h-16" />
                  <Skeleton className="w-full h-16" />
                  <Skeleton className="w-full h-16" />
                  <Skeleton className="w-full h-8" />
                  <div className="relative mt-2">
                    <Skeleton className="w-full h-12 rounded-md" />
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      <Skeleton className="w-6 h-6 rounded-md" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-md border p-6">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Skeleton className="w-32 h-6" />
                    <Skeleton className="w-8 h-8 rounded-full" />
                  </div>
                  <Skeleton className="w-full h-40" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  if (!flow) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold">Flow not found</h2>
          <p className="text-muted-foreground mt-2">This flow might have been deleted or you don't have access to it.</p>
          <Button className="mt-4" onClick={() => router.push('/flows')}>Go back to flows</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen overflow-hidden flex flex-col">
      <FlowHeader
        flowName={flow?.name}
        onBack={handleBack}
        isLoading={isLoadingFlow}
        flowId={flowId}
        isOwner={isOwner}
        isShared={flow?.is_shared}
        isAuthenticated={isAuthenticated}
        hasSchedule={!!schedule}
        initialStatus={flowStatus}
      />
      
      <div className="flex-1 overflow-auto">
        <div className="w-full px-6 py-6">
          {isOwner ? (
            <Tabs 
              defaultValue="overview" 
              className="w-full"
              onValueChange={(value) => setActiveTab(value)}
            >
              <div className="mb-6">
                <TabsList className="h-auto gap-4 rounded-none bg-transparent px-0 py-0 text-foreground">
                  <TabsTrigger 
                    className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                    value="overview"
                  >
                    Overview
                  </TabsTrigger>
                  <TabsTrigger 
                    className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                    value="schedule"
                  >
                    Schedule
                  </TabsTrigger>
                  <TabsTrigger 
                    className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                    value="flow-runs"
                  >
                    Flow Runs
                  </TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="overview" className="mt-0">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <FlowOverview description={flow.description} tools={usedTools} />
                  <FlowApiDocs 
                    flowName={flow.name}
                    flowId={flow.id}
                    isOwner={isOwner}
                    isAuthenticated={isAuthenticated}
                  />
                </div>
              </TabsContent>

              <TabsContent value="flow-runs" className="mt-0">
                <div className="bg-white rounded-md border p-6">
                  <h2 className="text-lg font-medium text-foreground">Runs</h2>
                  {schedule ? (
                    <ScheduleView
                      schedule={schedule}
                      flowName={flow?.name || ""}
                      flowRuns={flowRuns}
                    />
                  ) : (
                    <div className="text-muted-foreground">No schedule configured for this flow.</div>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="schedule" className="mt-0">
                <div className="bg-white rounded-md border p-6">
                  <ScheduleTabContent 
                    flowId={flowId}
                    isLoading={isLoadingFlow}
                    onScheduleChange={(newSchedule: FlowSchedule | null) => {
                      setSchedule(newSchedule);
                      if (activeTab === "flow-runs") {
                        loadScheduleAndRuns();
                      }
                    }}
                  />
                </div>
              </TabsContent>
            </Tabs>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <FlowOverview description={flow.description} tools={usedTools} />
              <FlowApiDocs 
                flowName={flow.name}
                flowId={flow.id}
                isOwner={isOwner}
                isAuthenticated={isAuthenticated}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
