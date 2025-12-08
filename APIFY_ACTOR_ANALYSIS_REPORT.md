# Apify Actor Analysis Report
## MCP Website Tool Actor - clever_fashion/mcp-website-tool

**Analysis Date:** 2025-12-08  
**Actor ID:** `clever_fashion/mcp-website-tool`  
**Actor Name:** "MCP tools – Turn Any Website into an AI Tool in 60 Seconds"  
**Total Runs:** 42 runs  
**Last Run:** 11 minutes ago (Succeeded after 11s)

---

## 🔍 Executive Summary

The deployed actor on Apify is **functionally working** but has **critical code differences** from the local project. The most significant issue is the **browser cleanup bug** that causes the "Event loop is closed" warning you observed. The local project has fixes that are **not yet deployed**.

---

## ⚠️ Critical Differences Found

### 1. **Browser Cleanup Bug (CRITICAL - NOT DEPLOYED)**

**Status:** ❌ **FIXED LOCALLY, NOT DEPLOYED**

**Deployed Version (`mcp-website-tool/src/main.py:356`):**
```python
with browser_manager.safe_page() as page:
    # ... work ...
    browser_manager.close()  # ❌ Called INSIDE context
    return (actions, mcp_json, screenshot_data, preview_html, url)
```

**Local Version (`src/main.py:358-361`):**
```python
try:
    with browser_manager.safe_page() as page:
        # ... work ...
        return (actions, mcp_json, screenshot_data, preview_html, url)
finally:
    browser_manager.close()  # ✅ Called OUTSIDE context
```

**Impact:**
- **Deployed:** Causes "Event loop is closed! Is Playwright already stopped?" warning
- **Local:** Proper cleanup order prevents the warning

**Root Cause:**
When `browser_manager.close()` is called inside the `safe_page()` context, it stops Playwright's event loop. Then when the context manager exits, it tries to close the page, but the event loop is already closed, causing the warning.

---

### 2. **Error Handling Improvement (NOT DEPLOYED)**

**Status:** ❌ **IMPROVED LOCALLY, NOT DEPLOYED**

**Deployed Version (`mcp-website-tool/src/browser.py:128-131`):**
```python
except Exception as close_error:
    self.logger.warning(
        "Failed to close page",
        error=str(close_error)
    )
```

**Local Version (`src/browser.py:130-139`):**
```python
except Exception as close_error:
    error_msg = str(close_error)
    # Suppress the "Event loop is closed" warning as it's expected
    if "Event loop is closed" not in error_msg and "already stopped" not in error_msg:
        self.logger.warning(
            "Failed to close page",
            error=error_msg
        )
    # Silently handle the expected case where Playwright is already stopped
```

**Impact:**
- **Deployed:** Logs warning for expected "Event loop is closed" errors
- **Local:** Suppresses expected warnings, only logs unexpected errors

---

## ✅ Identical Areas

### 1. **Configuration Files**
Both versions have identical:
- `.actor/actor.json` - Actor specification
- `.actor/input_schema.json` - Input schema
- `.actor/dataset_schema.json` - Dataset schema
- `Dockerfile` - Docker configuration
- `requirements.txt` - Dependencies
- `pyproject.toml` - Project configuration

### 2. **Core Functionality**
- Both use Apify SDK v3 async patterns (`async with Actor`)
- Both use Playwright for browser automation
- Both have the same extraction and MCP generation logic
- Both have the same error handling structure

### 3. **Dependencies**
Both specify:
- `apify>=2.0.0,<3.0.0` (but code uses v3 patterns - see warning below)
- `playwright>=1.40.0`
- `pydantic>=2.0.0,<2.10.0`
- `structlog>=23.0.0`

---

## ⚠️ Potential Issues

### 1. **Apify SDK Version Mismatch**

**Issue:** Both versions specify `apify>=2.0.0,<3.0.0` in dependencies, but the code uses Apify SDK v3 async patterns:
- `async with Actor:` (v3 pattern)
- `await Actor.get_input()` (v3 pattern)
- `await Actor.open_key_value_store()` (v3 pattern)

**Impact:** 
- May work if Apify base image includes v3 SDK
- Could cause runtime errors if v2 SDK is installed
- Dependency constraint is incorrect

**Recommendation:**
- Update `requirements.txt` to: `apify>=3.0.0,<4.0.0`
- Update `pyproject.toml` to: `"apify>=3.0.0,<4.0.0"`

### 2. **Recent Runs Show 0 Results**

**Observation:** All recent runs show "Results: 0" in the CLI output:
```
│ lJf3lyLlUsPUjTdy4   Succeeded         0   $0.000   2025-12-02     3s │
```

**Possible Causes:**
1. Runs completed too quickly (3s) - might be failing early
2. Dataset not being populated correctly
3. Input validation issues
4. Browser cleanup issue causing early termination

**Recommendation:**
- Check run logs in Apify console
- Verify dataset is being populated
- Test with a simple URL to verify functionality

---

## 📊 File Comparison Summary

| File | Status | Notes |
|------|--------|-------|
| `src/main.py` | ⚠️ **DIFFERENT** | Local has browser cleanup fix |
| `src/browser.py` | ⚠️ **DIFFERENT** | Local has improved error handling |
| `src/extractor.py` | ✅ **IDENTICAL** | No differences |
| `src/mcp_generator.py` | ✅ **IDENTICAL** | No differences |
| `src/types.py` | ✅ **IDENTICAL** | No differences |
| `src/utils.py` | ✅ **IDENTICAL** | No differences |
| `.actor/actor.json` | ✅ **IDENTICAL** | No differences |
| `.actor/input_schema.json` | ✅ **IDENTICAL** | No differences |
| `.actor/dataset_schema.json` | ✅ **IDENTICAL** | No differences |
| `Dockerfile` | ✅ **IDENTICAL** | No differences |
| `requirements.txt` | ✅ **IDENTICAL** | No differences |
| `pyproject.toml` | ✅ **IDENTICAL** | No differences |

---

## 🎯 Recommendations

### **IMMEDIATE ACTIONS (High Priority)**

1. **Deploy Browser Cleanup Fix**
   - The local version has the fix for the "Event loop is closed" warning
   - Deploy to eliminate the warning from production runs
   - **Files to deploy:** `src/main.py`, `src/browser.py`

2. **Deploy Error Handling Improvement**
   - Suppress expected warnings, improve log clarity
   - **File to deploy:** `src/browser.py`

3. **Fix Apify SDK Version Constraint**
   - Update dependencies to match actual SDK version used
   - **Files to update:** `requirements.txt`, `pyproject.toml`

### **INVESTIGATION NEEDED (Medium Priority)**

4. **Investigate 0 Results in Recent Runs**
   - Check run logs in Apify console
   - Verify dataset population
   - Test with known-good URLs
   - May be related to browser cleanup issue

5. **Add Test Coverage for Cleanup**
   - The local project has `test_safe_page_handles_closed_context_gracefully`
   - Ensure this test passes before deploying

### **OPTIONAL IMPROVEMENTS (Low Priority)**

6. **Consider Adding Build Verification**
   - Add CI/CD to verify builds before deployment
   - Ensure tests pass before pushing

7. **Documentation Updates**
   - Update deployment docs with latest fixes
   - Document the browser cleanup pattern

---

## 📝 Deployment Checklist

Before deploying the fixes:

- [ ] Run all tests locally: `pytest`
- [ ] Verify browser cleanup fix works: `test_safe_page_handles_closed_context_gracefully`
- [ ] Update Apify SDK version in dependencies (if needed)
- [ ] Test locally with `test_local.py`
- [ ] Deploy using `apify push`
- [ ] Verify deployment in Apify console
- [ ] Run test execution with simple URL
- [ ] Verify no "Event loop is closed" warning in logs
- [ ] Verify dataset is populated correctly

---

## 🔗 References

- **Actor URL:** https://console.apify.com/actors/clever_fashion~mcp-website-tool
- **Actor ID:** `clever_fashion/mcp-website-tool`
- **Local Project:** `F:\AI Projects\mcp-website-tool`
- **Pulled Actor:** `F:\AI Projects\mcp-website-tool\mcp-website-tool`

---

## 📌 Summary

**Current Status:** The deployed actor is functional but has the browser cleanup bug that causes the "Event loop is closed" warning. The local project has fixes that need to be deployed.

**Key Finding:** The warning you observed is caused by improper cleanup order in the deployed version. The local version has the fix but it hasn't been deployed yet.

**Action Required:** Deploy the browser cleanup fixes from the local project to eliminate the warning and improve error handling.

---

**Report Generated:** 2025-12-08  
**Analyst:** AI Code Assistant  
**Method:** Apify CLI + Direct File Comparison

