import json
import sys

def check_pyyaml():
    try:
        import yaml
        return True
    except ImportError:
        return False

if check_pyyaml():
    import yaml
    from flight_rest import app
    with open("FlightApi.yaml", "w", encoding="utf-8") as f:
        yaml.dump(app.openapi(), f, default_flow_style=False, sort_keys=False)
    print("Generated FlightApi.yaml using PyYAML")
else:
    from flight_rest import app
    with open("swagger.json", "w", encoding="utf-8") as f:
        json.dump(app.openapi(), f, indent=2)
    print("Generated swagger.json (PyYAML not installed)")
