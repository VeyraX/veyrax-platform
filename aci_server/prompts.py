import json
from datetime import date

def get_parameter_generation_prompt(tool: str, method: str, question: str, tool_schema: dict) -> str:
    today = date.today().isoformat()
    
    prompt = f"""
Today's date is {today}.

Given the user's question: "{question}"

And the available tool '{tool}' with method '{method}', which has the following schema:
{json.dumps(tool_schema, indent=2)}

Generate the JSON parameters required to call the '{method}' function to address the user's question based *only* on the provided information (question, schema, today's date).
Only output the JSON object containing the parameters. Do not include any explanations, apologies, or surrounding text.
If no parameters are needed, output an empty JSON object {{}}.
If you cannot determine the parameters from the question and schema, output an empty JSON object {{}}.
"""
    return prompt 