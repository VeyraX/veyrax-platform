from aci_components import BaseComponent

class JiraTransitionsList(BaseComponent):
    type = "JiraTransitionsList"
    field_mapping = {
        "id": "id",
        "name": "name",
        "status": "to_status.name",
        "status_category": "to_status.category.name",
        "available": "is_available"
    }
    columns = [
        {"name": "Transition", "field": "name"},
        {"name": "Target Status", "field": "status"},
        {"name": "Category", "field": "status_category"},
        {"name": "Available", "field": "available", "type": "boolean"}
    ]
    operations = [
        {"name": "transition", "label": "Execute Transition", "type": "action"}
    ] 