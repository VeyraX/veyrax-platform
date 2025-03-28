import { ImageResponse } from '@vercel/og';
import { getPublicFlowById, getPublicFlowActions, getActionsByIds } from '@/app/modules/flows/api/api.flows';

export const runtime = 'edge';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const flowId = searchParams.get('flowId');

    if (!flowId) {
      return new Response('Flow ID is required', { status: 400 });
    }

    // Get flow data
    const flow = await getPublicFlowById(flowId);
    if (!flow) {
      return new Response('Flow not found', { status: 404 });
    }

    // Get flow actions
    const actionIds = await getPublicFlowActions(flowId);
    const actions = await getActionsByIds(actionIds);

    // Remove duplicate tools
    const uniqueTools = actions
      .map(action => ({
        name: action.provider_name,
        logoUrl: action.logo_url
      }))
      .filter((tool, index, self) =>
        index === self.findIndex((t) => t.name === tool.name)
      );

    return new ImageResponse(
      (
        <div style={{
          width: '1200px',
          height: '630px',
          backgroundColor: 'white',
          padding: '64px',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
        }}>
          {/* Enhanced background particles */}
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              style={{
                position: 'absolute',
                width: i % 3 === 0 ? '6px' : '4px',
                height: i % 3 === 0 ? '6px' : '4px',
                backgroundColor: i % 5 === 0 ? '#e5e7eb' : '#f3f4f6',
                borderRadius: '50%',
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
                opacity: Math.random() * 0.8 + 0.2,
              }}
            />
          ))}
          {/* Additional larger particles for depth */}
          {[...Array(15)].map((_, i) => (
            <div
              key={`large-${i}`}
              style={{
                position: 'absolute',
                width: '8px',
                height: '8px',
                backgroundColor: '#e5e7eb',
                borderRadius: '50%',
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
                opacity: 0.4,
              }}
            />
          ))}

          {/* Header with logo and tools */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            width: '100%',
            marginBottom: '40px',
          }}>
            {/* Logo */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
            }}>
              <svg width="60" height="60" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="50" fill="black"/>
                <path d="M23.5126 47.2249C23.5126 44.065 25.494 41.2444 28.4665 40.1726L78.8672 22V30.9659L32.8683 47.2604L78.8672 63.5549V72.5208L28.4577 54.274C25.4897 53.1996 23.5126 50.3813 23.5126 47.2249V47.2249Z" fill="white"/>
                <path d="M48.2419 57.4032V57.4032C50.4093 51.1732 50.4954 44.4079 48.4871 38.1248L48.4177 37.9075L46.8814 36.8899L46.668 58.0333L48.2419 57.4032Z" fill="white"/>
                <path d="M47.2249 77.3838C44.065 77.3838 41.2444 75.4025 40.1726 72.43L22 22.0293H30.9659L47.2604 68.0281L63.5549 22.0293L72.5208 22.0293L54.274 72.4388C53.1996 75.4067 50.3813 77.3838 47.2249 77.3838V77.3838Z" fill="white"/>
              </svg>
            </div>

            {/* Tool icons */}
            <div style={{
              display: 'flex',
              gap: '12px',
              alignItems: 'center',
            }}>
              {uniqueTools.map((tool, index) => (
                <div
                  key={index}
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    overflow: 'hidden',
                    backgroundColor: '#f3f4f6',
                    display: 'flex',
                  }}
                >
                  <img
                    src={tool.logoUrl}
                    alt={tool.name}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                    }}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Flow Title and Subtitle */}
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}>
            <h1 style={{
              fontSize: '64px',
              fontWeight: 'bold',
              color: 'black',
              lineHeight: '1.2',
              letterSpacing: '-0.02em',
              marginBottom: '16px',
              margin: 0,
            }}>
              {flow.name}
            </h1>
            <p style={{
              fontSize: '24px',
              color: '#4B5563',
              letterSpacing: '-0.02em',
              margin: 0,
            }}>
              Create your own Agent Flow with VeyraX
            </p>
          </div>

          {/* Website URL at bottom left */}
          <div style={{
            position: 'absolute',
            bottom: '32px',
            left: '64px',
            fontSize: '18px',
            color: '#6B7280',
            letterSpacing: '-0.01em',
          }}>
            veyrax.com
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
      },
    );
  } catch (error) {
    console.error('Error generating OG image:', error);
    return new Response('Failed to generate image', { status: 500 });
  }
} 