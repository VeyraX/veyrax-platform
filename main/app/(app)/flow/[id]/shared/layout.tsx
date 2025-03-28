import { Metadata } from 'next';
import { getPublicFlowById } from "@/app/modules/flows/api/api.flows";

export async function generateMetadata(
  { params }: { params: { id: string } }
): Promise<Metadata> {
  const flow = await getPublicFlowById(params.id);
  
  if (!flow) {
    return {
      title: 'Flow Not Found',
      description: 'The requested flow could not be found.',
    };
  }

  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://veyrax.com';
  const ogImageUrl = `${baseUrl}/api/og?flowId=${params.id}`;
  
  const description = flow.plain_description 
    ? flow.plain_description.slice(0, 70) + (flow.plain_description.length > 70 ? '...' : '')
    : `Check out this flow: ${flow.name}`;

  return {
    metadataBase: new URL(baseUrl),
    title: flow.name,
    description: description,
    openGraph: {
      title: flow.name,
      description: description,
      type: 'website',
      url: `${baseUrl}/flow/${params.id}/shared`,
      images: [{
        url: ogImageUrl,
        width: 1200,
        height: 630,
        alt: flow.name
      }]
    },
    twitter: {
      card: 'summary_large_image',
      title: flow.name,
      description: description,
      images: [ogImageUrl],
    }
  };
}

export default function SharedFlowLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}