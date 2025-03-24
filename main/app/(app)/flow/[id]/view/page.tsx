"use client";

import FlowViewPage from "@/app/modules/flows/pages/flow-view-page";

export default function FlowViewPageWrapper({ params }: { params: { id: string } }) {
  return <FlowViewPage flowId={params.id} />;
} 