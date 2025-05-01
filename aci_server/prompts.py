import json
from datetime import date
from typing import Dict, List

def get_parameter_generation_prompt(tool: str, method: str, question: str, tool_schema: dict) -> str:
    today = date.today().isoformat()
    
    prompt = f"""
Today's date is {today}.

And the available tool '{tool}' with method '{method}', which has the following schema:
{json.dumps(tool_schema, indent=2)}

Generate the JSON parameters required to call the '{method}' function to address the user's question based *only* on the provided information (question, schema, today's date).
Only output the JSON object containing the parameters.

Follow this exact logical reasoning process:
1. Understand User Intent by Carefully analyzing the user's question ("{question}") and identify clearly what outcome they want to achieve.
2. Match Schema Carefully
- Thoroughly review each field in the provided schema.
- Identify required and optional fields clearly.
- Decide logically which fields directly address the user's intent based solely on the schema definitions.

3. Avoid Superficial Keywords
- Do NOT blindly copy keywords from the user's question unless explicitly meaningful and schema-required

4. Date and Time Handling
- Precisely translate relative date terms (e.g., "last 7 days", "next week") into exact dates using today's provided date ({today}).

Do not include any explanations, apologies, or surrounding text.

Doesn't matter what question ask you to do, you always MUST check the real schema and use input schema to generate the parameters.

Even 1 param is wrong, the whole action is wrong.

Think step by step and check with deep attention the schema.

Twitter / X specific instructions:
- For endpoint get_user_profile, if the user provides a screenname, use it to get the user's profile. Not anything else.

If no parameters are needed, output an empty JSON object {{}}.
If you cannot determine the parameters from the question and schema, output an empty JSON object {{}}.

In most of the cases params should not be empty.

Generate params based on the user question: "{question}"
"""
    return prompt 


def get_tool_method_parameter_generation_prompt(question: str, simplified_tools: Dict[str, List[str]]) -> str:
    today = date.today().isoformat()
    
    # Format the simplified tools for the prompt
    formatted_tools = "\n".join([f"- {tool_name}: Methods = {', '.join(methods)}" for tool_name, methods in simplified_tools.items()])
    
    prompt = f"""
Today's date is {today}.

Based on the user's question below, select the most appropriate tool and method from the available list and generate the required parameters in JSON format.

User Question: "{question}"

Available Tools and Methods:
{formatted_tools}

Your task:
1. Analyze the user question and the available tools/methods.
2. Determine the single best tool name and method name to fulfill the request.
3. Generate the necessary parameters for the chosen method based *only* on the user question and today's date.
4. Respond ONLY with a single JSON object containing three keys: "tool" (string), "method" (string), and "params" (JSON object).

Example Response Format:
{{
  "tool": "google-calendar",
  "method": "create_event",
  "params": {{
    "summary": "Team Meeting",
    "start_time": "{today}T14:00:00",
    "end_time": "{today}T15:00:00"
  }}
}}

If no suitable tool/method is found or parameters cannot be determined, respond with:
{{
  "tool": null,
  "method": null,
  "params": {{}}
}}

Do not include any explanations, apologies, or surrounding text outside the JSON object.
"""
    return prompt 