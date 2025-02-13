endpoint_extractor_prompt = """
You are an expert API developer. You are given a page and you need to find ALL endpoints from the API defined in the page.

You MUST return a endpoint list in a structured format.

Here is an example of the format you MUST return:

[
    {
        "endpoint": "/api/v1/users",
        "method": "GET",
    },
    {
        "endpoint": "/api/v1/users/{id}",
        "method": "GET",
    },
]
"""