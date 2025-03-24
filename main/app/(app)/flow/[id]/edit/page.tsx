"use client";

import FlowCreatePage from "@/app/modules/flows/pages/flow-create-page";

export default function FlowEditPageWrapper({ params }: { params: { id: string } }) {
  return <FlowCreatePage flowId={params.id} />;
} 