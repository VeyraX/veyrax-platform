import React from 'react';

const backendResponse = {
  tool: "outlook_event",
  data: {
    subject: "Встреча с командой",
    start: {
      dateTime: "2024-03-20T10:00:00",
      timeZone: "UTC"
    },
    end: {
      dateTime: "2024-03-20T11:00:00",
      timeZone: "UTC"
    },
    web_link: "https://example.com/meeting",
    organizer: {
      emailAddress: {
        name: "Иван Петров",
        address: "ivan@example.com"
      }
    }
  },
  component: {
    name: "EventCard",
    code: `
      return function({ subject, start, end, web_link, organizer }) {
        const startDate = start ? new Date(start.dateTime) : new Date();
        const endDate = end ? new Date(end.dateTime) : new Date();

        const formatTime = (date) => {
          return date.toLocaleTimeString("en-US", {
            hour: "numeric",
            minute: "2-digit",
            hour12: true,
            timeZone: start?.timeZone || 'UTC'
          }).replace(/\\s/g, '');
        }

        const organizerName = organizer?.emailAddress?.name || 'Unknown';

        return React.createElement('div', 
          { className: "w-[300px] inline-block mr-3 border rounded-lg" },
          React.createElement('div', 
            { className: "p-3 flex flex-col" },
            React.createElement('div', 
              { className: "flex items-center justify-between gap-2 mb-2" },
              React.createElement('div', 
                { className: "flex items-center gap-2 flex-1 min-w-0" },
                React.createElement('span', 
                  { className: "truncate text-sm font-medium" },
                  subject
                )
              ),
              web_link && React.createElement('a', 
                { 
                  href: web_link,
                  target: "_blank",
                  rel: "noopener noreferrer"
                },
                React.createElement('span', null, '🔗')
              )
            ),
            React.createElement('div', 
              { className: "text-xs text-gray-500" },
              \`\${formatTime(startDate)} - \${formatTime(endDate)} • \${organizerName}\`
            )
          )
        );
      }
    `
  }
};

function createComponent(componentCode: string) {
  try {
    return new Function('React', componentCode)(React);
  } catch (error) {
    console.error('Ошибка при создании компонента:', error);
    return () => <div>Ошибка рендеринга компонента</div>;
  }
}

function renderDynamicComponent(response: typeof backendResponse) {
  try {
    const { data, component } = response;
    const DynamicComponent = createComponent(component.code);
    return <DynamicComponent {...data} />;
  } catch (error) {
    console.error('Ошибка при рендеринге:', error);
    return <div>Ошибка при рендеринге компонента</div>;
  }
}

const backendResponses = [
  {
    tool: "outlook_event",
    data: {
      subject: "Встреча с командой разработки",
      start: {
        dateTime: "2024-03-20T10:00:00",
        timeZone: "UTC"
      },
      end: {
        dateTime: "2024-03-20T11:00:00",
        timeZone: "UTC"
      },
      web_link: "https://example.com/meeting1",
      organizer: {
        emailAddress: {
          name: "Иван Петров",
          address: "ivan@example.com"
        }
      }
    },
    component: {
      name: "EventCard",
      code: backendResponse.component.code
    }
  },
  {
    tool: "outlook_event",
    data: {
      subject: "Планирование спринта",
      start: {
        dateTime: "2024-03-20T14:00:00",
        timeZone: "UTC"
      },
      end: {
        dateTime: "2024-03-20T15:30:00",
        timeZone: "UTC"
      },
      web_link: "https://example.com/meeting2",
      organizer: {
        emailAddress: {
          name: "Мария Сидорова",
          address: "maria@example.com"
        }
      }
    },
    component: {
      name: "EventCard",
      code: backendResponse.component.code
    }
  },
  {
    tool: "outlook_event",
    data: {
      subject: "Ретроспектива проекта",
      start: {
        dateTime: "2024-03-21T11:00:00",
        timeZone: "UTC"
      },
      end: {
        dateTime: "2024-03-21T12:00:00",
        timeZone: "UTC"
      },
      web_link: "https://example.com/meeting3",
      organizer: {
        emailAddress: {
          name: "Алексей Кузнецов",
          address: "alex@example.com"
        }
      }
    },
    component: {
      name: "EventCard",
      code: backendResponse.component.code
    }
  }
];

export default function TestPage() {
  return (
    <div className="p-4">
      <h1 className="text-xl mb-4">Динамический рендеринг компонентов</h1>
      <div className="flex flex-wrap gap-4">
        {backendResponses.map((response, index) => (
          <div key={index}>
            {renderDynamicComponent(response)}
          </div>
        ))}
      </div>
    </div>
  );
}

interface ComponentDefinition {
  name: string;
  code: string;
}

interface BackendResponse {
  tool: string;
  data: Record<string, any>;
  component: ComponentDefinition;
}
