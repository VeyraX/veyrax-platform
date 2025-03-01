# examples_handler.py

import os
import yaml
import warnings
from typing import Dict, Any, List, Optional, Tuple
import inspect

class ExamplesLoader:
    """
    Loads examples from a default 'examples.yaml' file in the same directory (or 
    another default path), storing them internally for quick access by route name.
    """
    def __init__(
        self,
        integration_dir: Optional[str] = None,
        yaml_filename: str = "examples.yaml",
        top_key: str = "routes"
    ):
        """
        Args:
            integration_dir: Directory where examples.yaml is located. If None, uses 
                            the directory of the calling file by default.
            yaml_filename:   The name of the YAML file to load (defaults to 'examples.yaml').
            top_key:         The top-level key in YAML that holds your route definitions 
                            (defaults to 'routes').
        """
        if integration_dir is None:
            # Get the directory of the calling file (not this file)
            caller_frame = inspect.stack()[1]
            integration_dir = os.path.dirname(os.path.abspath(caller_frame.filename))
        
        self.examples_file = os.path.join(integration_dir, yaml_filename)
        self.top_key = top_key
        self._route_map: Dict[str, List[Dict[str, Any]]] = {}
        
        self._load_file()

    def __getitem__(self, route_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Allows for dictionary-like access with square brackets notation:
        examples["/confluence/spaces"]
        """
        return self.get(route_name)

    def _load_file(self) -> None:
        """Reads the YAML file and populates an internal route -> examples map."""
        if not os.path.exists(self.examples_file):
            # No file found, leave route map empty
            return
        
        with open(self.examples_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        
        endpoints_list = data.get(self.top_key, [])
        
        for route_info in endpoints_list:
            endpoint_path = route_info.get("endpoint")
            scenario_list = route_info.get("examples", [])
            if endpoint_path:
                self._route_map[endpoint_path] = scenario_list

    def _find_similar_route(self, route_name: str) -> Optional[str]:
        """
        Check if the given route name might be a misspelling of an existing route.
        Uses a simple string similarity check to find potential matches.
        
        Returns the most similar route name if found, otherwise None.
        """
        if not self._route_map:
            return None
        
        # Simple implementation using character-level difference
        def similarity(s1: str, s2: str) -> int:
            """Return a score of how similar two strings are (lower is more similar)"""
            # Simple case-insensitive check
            if s1.lower() == s2.lower():
                return 0
                
            # Check for simple character differences
            # This is a very basic implementation - not a full Levenshtein distance
            # We're just looking for obvious typos
            max_len = max(len(s1), len(s2))
            min_len = min(len(s1), len(s2))
            
            # If lengths are very different, probably not a typo
            if max_len > min_len * 2:
                return max_len
                
            # Count character differences
            diff = 0
            for i in range(min(len(s1), len(s2))):
                if s1[i] != s2[i]:
                    diff += 1
            
            # Add penalty for length difference
            diff += abs(len(s1) - len(s2))
            
            return diff
        
        # Find closest match
        closest_route = None
        closest_score = 3  # Maximum difference to consider a potential typo
        
        for existing_route in self._route_map.keys():
            score = similarity(route_name, existing_route)
            if score <= closest_score:
                closest_score = score
                closest_route = existing_route
                
        return closest_route

    def get(self, route_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Returns a list of example definitions for the specified route name 
        (like '/confluence/spaces'), or None if no examples are found.
        """
        examples = self._route_map.get(route_name)
        if examples is None:
            similar_route = self._find_similar_route(route_name)
            if similar_route:
                warnings.warn(f"No examples found for route: {route_name}. Did you mean '{similar_route}'?")
            else:
                warnings.warn(f"No examples found for route: {route_name}")
        return examples

#
# Optional: Show usage if running directly
#
if __name__ == "__main__":
    # If you run this file directly, just to demonstrate how it works:
    loader = ExamplesLoader()  # defaults to 'examples.yaml' in same directory
    # Can now use both styles:
    examples1 = loader.get("/confluence/spaces")
    examples2 = loader["/confluence/spaces"]
    
    # Test with a non-existent route to see the warning
    missing_examples = loader["/non/existent/route"]
    
    # Test with a misspelled route
    misspelled_examples = loader["/confluence/spcaes"]  # Typo in "spaces"
    
    if examples1:
        print(f"Found {len(examples1)} scenario(s) for /confluence/spaces")
        for scenario in examples1:
            print("Scenario:", scenario.get("scenario"))
            print("Input JSON:", scenario.get("input_json"))
            print("Output JSON:", scenario.get("output_json"))
            print("---")
    else:
        print("No examples found for /confluence/spaces.")
