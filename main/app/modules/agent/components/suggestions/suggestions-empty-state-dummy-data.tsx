export const getToolQuestions = (connectedTools: string[]) => {
  const allToolQuestions = [
    {
      toolName: "gmail",
      questions: [
        "Find all emails containing specific keywords in my inbox",
        "Draft a professional email with specific content",
        "Send an important email from my drafts"
      ]
    },
    {
      toolName: "google-calendar",
      questions: [
        "Find events matching specific criteria in my calendar",
        "Schedule a new meeting with team members",
        "Check my calendar for availability in a specific timeframe"
      ]
    },
    {
      toolName: "google-drive",
      questions: [
        "Search for specific files across my Google Drive",
        "Find documents containing specific content",
        "Organize files by moving them between folders"
      ]
    },
    {
      toolName: "notion",
      questions: [
        "Search across all my Notion pages for specific content",
        "Create a new page in a specific database",
        "Find and read details from a specific Notion page"
      ]
    },
    {
      toolName: "linear",
      questions: [
        "Create a new issue with specific details",
        "Find issues matching certain criteria",
        "Update the status of an existing issue"
      ]
    },
    {
      toolName: "perplexity",
      questions: [
        "Research a complex topic and provide detailed information",
        "Explain a technical concept in simple terms",
        "Analyze and summarize recent developments in a field"
      ]
    },
    {
      toolName: "openweather",
      questions: [
        "Get the current weather for a specific city",
        "Check the weather forecast for my location",
        "Find out the weather conditions in another country"
      ]
    },
    {
      toolName: "jira",
      questions: [
        "Find issues assigned to me in a project",
        "Create a new task with specific details",
        "Update the status of an existing issue"
      ]
    },
    {
      toolName: "confluence",
      questions: [
        "Search for pages containing specific content",
        "Find documentation in a specific space",
        "Get details from a specific Confluence page"
      ]
    },
    {
      toolName: "outlook",
      questions: [
        "Find emails containing specific keywords in my Outlook inbox",
        "Draft a new email with specific content in Outlook",
        "Check my Outlook calendar for upcoming meetings",
        "Schedule a new meeting with team members in Outlook"
      ]
    },
    {
      toolName: "dropbox",
      questions: [
        "Find recent files in my Dropbox",
        "Search for specific documents in my Dropbox",
        "Get information about a file in my Dropbox",
        "List files in a specific Dropbox folder"
      ]
    },
    {
      toolName: "slack",
      questions: [
        "Find recent messages in a Slack channel",
        "Search for specific content in Slack conversations",
        "Get information about a Slack channel",
        "Find messages from a specific person in Slack"
      ]
    },
    {
      toolName: "browser-use",
      questions: [
        "Search for information on a specific website",
        "Find recent browser history",
        "Open a specific webpage and extract information",
        "Analyze the content of a webpage"
      ]
    },
    {
      toolName: "resend",
      questions: [
        "Send an email with specific content",
        "Find recent emails in my Resend inbox",
        "Get information about a specific email in Resend",
        "Find emails from a specific person in Resend"
      ]
    }
  ]

  return allToolQuestions.filter(tool => 
    connectedTools.includes(tool.toolName)
  )
}