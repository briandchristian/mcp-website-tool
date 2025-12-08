# Step 3: Fix Apify SDK Version Constraint

## Issue
Dependencies specified `apify>=2.0.0,<3.0.0` but code uses Apify SDK v3 async patterns.

## Code Evidence (v3 Patterns)
```python
# src/main.py
async with Actor:  # v3 pattern
    actor_input = await Actor.get_input()  # v3 pattern
    key_value_store = await Actor.open_key_value_store()  # v3 pattern
    await Actor.push_data(result_data)  # v3 pattern
```

## Changes Made

### 1. requirements.txt
**Before:**
```
apify>=2.0.0,<3.0.0
```

**After:**
```
apify>=3.0.0,<4.0.0
```

### 2. pyproject.toml
**Before:**
```toml
dependencies = [
    "apify>=2.0.0,<3.0.0",
    ...
]
```

**After:**
```toml
dependencies = [
    "apify>=3.0.0,<4.0.0",
    ...
]
```

## Impact

### Why This Matters
1. **Explicit Dependency**: Makes it clear the code requires v3 SDK
2. **Future-Proofing**: If base image changes, explicit constraint ensures compatibility
3. **Documentation**: Other developers can see the required SDK version
4. **Build Verification**: pip/poetry will verify the correct version is available

### Base Image Note
The Dockerfile uses `apify/actor-python-playwright:3.11` which includes Apify SDK v3. However, having an explicit constraint:
- Documents the requirement
- Ensures compatibility if base image changes
- Helps with local development

## Testing
After deployment, verify:
1. Actor builds successfully
2. No import errors
3. All async patterns work correctly
4. Dataset push completes successfully

## Status
✅ **FIXED** - Version constraints updated to match code requirements

