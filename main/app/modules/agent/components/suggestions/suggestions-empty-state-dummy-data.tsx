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
    }
  ]

  return allToolQuestions.filter(tool => 
    connectedTools.includes(tool.toolName)
  )
}