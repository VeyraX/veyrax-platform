from datetime import datetime


today_day = datetime.now().strftime("%Y-%m-%d")

get_tools_example_prompt = f"""
{{
  "instruction": "Here is a structure of the prompt that you should follow to call and execute tools properly. You MUST call tool, method and relevant parameters depends on the tool, method and user question. For G-Tools pagination, simply use page number. The date is today's date: {today_day}. If user requested a tool that is not available, please call veyrax-auth tool to check if requested tool is avaliable at all on the platform and generate a connection url for the tool.",
  "examples": [
    {{
    "user_question": "I need to find a 5 pages in Confluence about the API documentation. Please search for it.",
    "tool": "confluence",
    "method": "search_content",
    "parameters": {{
        "cql": null,
        "space_key": null,
        "title": "API",
        "type": "page",
        "limit": 5
        }}
    }},
    {{
      "user_question": "I need to find quarterly report in my emails between 2023-01-01 and 2023-12-31. Please search for it.",
      "tool": "gmail",
      "method": "get_messages",
      "parameters": {{
          "pageToken": null,
          "filters": {{
            "body_keywords": "quarterly report",
            "recipient": null,
            "subject_keywords": "quarterly report",
            "after_date": "2023-01-01",
            "before_date": "2023-12-31",
            "max_results": 5
          }}
        }}
    }},
    {{
      "user_question": "Show me the next page of available tools",
      "page": 2
    }}
  ]
}}
"""


get_tools_example_prompt_empty = f"""
{{
  "instruction": "User doesn't have any active tools. Provide guidance to go to VeryX platform and setup integrations: https://veyrax.com/integrations The date is today's date: {today_day}",
  "examples": []
}}
"""
