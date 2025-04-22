import { Metadata } from "next";
import McpViewPage from "@/app/modules/integrations/pages/mcp-page-detail";

export const generateMetadata = ({ params }: { params: { image_name: string } }): Metadata => {
  const { image_name } = params;
  
  return {
    title: `${image_name} | VeyraX MCP`,
    description: `Details and configuration for the ${image_name} MCP`,
  };
};

export default function McpDetailPage({ params }: { params: { image_name: string } }) {
  const { image_name } = params;
  
  return <McpViewPage imageName={image_name} isPublic={true} />;
}
