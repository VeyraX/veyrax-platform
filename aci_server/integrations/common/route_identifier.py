from fastapi import routing

def route_identifier(route: routing.APIRoute) -> str:
    """
    Extract a consistent identifier for a route that can be used to match
    between frontend tool calls and backend route handlers.
    
    Returns the route path, which provides a consistent way to identify routes
    across the application.
    """
    path = str(route.path)
    if "/" == path[0]:
        return path[1:]
    return path

def route_tool(route: routing.APIRoute) -> str:
    """
    Extract a consistent identifier for a route that can be used to match
    between frontend tool calls and backend route handlers.
    
    Returns the route path, which provides a consistent way to identify routes
    across the application.
    """
    return route_identifier(route).split('/')[0]

def route_method(route: routing.APIRoute) -> str:
    """
    Extract a consistent identifier for a route that can be used to match
    between frontend tool calls and backend route handlers.
    
    Returns the route path, which provides a consistent way to identify routes
    across the application.
    """
    return route_identifier(route).split('/')[1]