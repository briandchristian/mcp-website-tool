"""
Validate Actor configuration against Apify requirements.
This script checks all required files and configurations without publishing.
"""
import json
import sys
from pathlib import Path

def validate_json_file(filepath: Path, description: str) -> tuple[bool, str]:
    """Validate a JSON file exists and is valid."""
    if not filepath.exists():
        return False, f"{description} not found: {filepath}"
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True, f"✓ {description} is valid"
    except json.JSONDecodeError as e:
        return False, f"{description} has invalid JSON: {e}"

def validate_actor_json():
    """Validate actor.json structure."""
    actor_path = Path(".actor/actor.json")
    success, message = validate_json_file(actor_path, "actor.json")
    if not success:
        return False, message
    
    with open(actor_path, 'r') as f:
        actor = json.load(f)
    
    required_fields = ["actorSpecification", "name", "version", "title"]
    missing = [field for field in required_fields if field not in actor]
    if missing:
        return False, f"actor.json missing required fields: {missing}"
    
    # Check version format (MAJOR.MINOR)
    version = actor.get("version", "")
    if version and "." in version:
        parts = version.split(".")
        if len(parts) != 2 or not all(p.isdigit() and 0 <= int(p) <= 99 for p in parts):
            return False, f"actor.json version must be MAJOR.MINOR (0-99): {version}"
    
    # Check input schema reference
    input_ref = actor.get("input", "")
    input_path = Path(".actor/input_schema.json")
    if not input_path.exists():
        return False, f"Input schema not found at: {input_path}"
    
    # Check dataset schema reference
    dataset_ref = actor.get("storages", {}).get("dataset", "")
    dataset_path = Path(".actor/dataset_schema.json")
    if dataset_ref and not dataset_path.exists():
        return False, f"Dataset schema not found at: {dataset_path}"
    
    return True, "✓ actor.json structure is valid"

def validate_input_schema():
    """Validate input_schema.json structure."""
    schema_path = Path(".actor/input_schema.json")
    success, message = validate_json_file(schema_path, "input_schema.json")
    if not success:
        return False, message
    
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    # Check required fields
    if "schemaVersion" not in schema:
        return False, "input_schema.json missing schemaVersion"
    if "properties" not in schema:
        return False, "input_schema.json missing properties"
    if "required" not in schema:
        return False, "input_schema.json missing required array"
    
    # Check each property has editor (for string/array types)
    for prop_name, prop_def in schema.get("properties", {}).items():
        prop_type = prop_def.get("type")
        if prop_type in ["string", "array"]:
            if "editor" not in prop_def:
                return False, f"input_schema.json: property '{prop_name}' (type: {prop_type}) missing 'editor' field"
    
    return True, "✓ input_schema.json structure is valid"

def validate_dataset_schema():
    """Validate dataset_schema.json structure."""
    schema_path = Path(".actor/dataset_schema.json")
    success, message = validate_json_file(schema_path, "dataset_schema.json")
    if not success:
        return False, message
    
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    # Check required fields
    if "actorSpecification" not in schema:
        return False, "dataset_schema.json missing actorSpecification"
    if "fields" not in schema:
        return False, "dataset_schema.json missing fields"
    if "views" not in schema:
        return False, "dataset_schema.json missing views"
    
    # Check views structure
    for view_name, view_def in schema.get("views", {}).items():
        if "transformation" not in view_def:
            return False, f"dataset_schema.json: view '{view_name}' missing transformation"
        if "display" not in view_def:
            return False, f"dataset_schema.json: view '{view_name}' missing display"
        
        # Check transformation doesn't have empty arrays that require minItems
        transformation = view_def.get("transformation", {})
        for array_field in ["omit", "unwind", "flatten"]:
            if array_field in transformation:
                arr = transformation[array_field]
                if isinstance(arr, list) and len(arr) == 0:
                    return False, f"dataset_schema.json: view '{view_name}' has empty '{array_field}' array (remove if not needed)"
        
        # Check display component is valid
        display = view_def.get("display", {})
        component = display.get("component")
        if component and component not in ["table", "grid"]:
            return False, f"dataset_schema.json: view '{view_name}' has invalid component '{component}' (must be 'table' or 'grid')"
    
    return True, "✓ dataset_schema.json structure is valid"

def validate_file_structure():
    """Validate required files exist."""
    required_files = [
        Path("README.md"),
        Path("pyproject.toml"),
        Path("src/main.py"),
        Path(".actor/actor.json"),
        Path(".actor/input_schema.json"),
        Path(".actor/dataset_schema.json"),
    ]
    
    missing = []
    for filepath in required_files:
        if not filepath.exists():
            missing.append(str(filepath))
    
    if missing:
        return False, f"Missing required files: {', '.join(missing)}"
    
    return True, "✓ All required files exist"

def main():
    """Run all validations."""
    print("=" * 60)
    print("Apify Actor Local Validation")
    print("=" * 60)
    print()
    
    all_passed = True
    validations = [
        ("File Structure", validate_file_structure),
        ("actor.json", validate_actor_json),
        ("input_schema.json", validate_input_schema),
        ("dataset_schema.json", validate_dataset_schema),
    ]
    
    for name, validator in validations:
        print(f"Validating {name}...")
        success, message = validator()
        print(f"  {message}")
        if not success:
            all_passed = False
        print()
    
    print("=" * 60)
    if all_passed:
        print("✓ All validations passed! Actor is ready for Apify.")
        return 0
    else:
        print("✗ Some validations failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

