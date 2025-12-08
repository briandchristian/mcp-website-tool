# Step 2: Investigation - Why Recent Runs Show 0 Results

## Analysis Date: 2025-12-08

## Observation
All recent Apify runs show "Results: 0" and complete very quickly (3 seconds):
```
│ lJf3lyLlUsPUjTdy4   Succeeded         0   $0.000   2025-12-02     3s │
```

## Possible Root Causes

### 1. **Browser Cleanup Bug (MOST LIKELY)**
**Status:** ✅ Fixed in local, ❌ Not deployed

The deployed version has `browser_manager.close()` called inside the `safe_page()` context, which:
- Closes Playwright event loop prematurely
- May cause the page context to fail during cleanup
- Could terminate the actor before `push_data()` is called
- Results in successful exit (0) but no data pushed

**Evidence:**
- Warning observed: "Event loop is closed! Is Playwright already stopped?"
- Runs complete in 3s (too fast for full execution)
- Status: Succeeded (not Failed) - suggests early termination

### 2. **Exception Before push_data()**
The code has proper error handling, but if an exception occurs:
- Before line 443 (`await Actor.push_data(result_data)`)
- The exception is logged and re-raised
- Actor exits with error (should show as Failed, not Succeeded)

**Check:** Run logs should show error messages if this is the case.

### 3. **Input Validation Failure**
If `InputModel(**actor_input)` fails:
- Exception would be caught at line 467
- Should show as Failed status
- Not consistent with "Succeeded" status

### 4. **Missing await on set_value()**
**CRITICAL FINDING:** Checking deployed version...

**Local Version (src/main.py:402):**
```python
await key_value_store.set_value(mcp_key, mcp_json)
```

**Deployed Version:** Need to verify this call exists.

If missing, the MCP JSON wouldn't be saved, but dataset push should still work.

### 5. **Apify SDK Version Mismatch**
Dependencies specify `apify>=2.0.0,<3.0.0` but code uses v3 patterns:
- `async with Actor:` (v3)
- `await Actor.get_input()` (v3)
- `await Actor.open_key_value_store()` (v3)

If v2 SDK is installed, these calls would fail.

## Recommended Actions

### Immediate
1. **Deploy browser cleanup fix** - This is the most likely cause
2. **Check run logs** in Apify console for the specific run IDs
3. **Verify dataset push** - Check if `push_data()` is being called

### Investigation Steps
1. Check Apify console logs for run `lJf3lyLlUsPUjTdy4`:
   - Look for "data_pushed" log message
   - Check for any exceptions
   - Verify browser extraction completed

2. Test with simple URL:
   - Run actor with `{"url": "https://example.com"}`
   - Monitor logs in real-time
   - Verify dataset is populated

3. Add more logging:
   - Log before and after `push_data()`
   - Log dataset push result
   - Add try/catch around `push_data()` to catch silent failures

## Code Flow Analysis

```
1. Actor starts (async with Actor)
2. Get input (await Actor.get_input())
3. Validate input (InputModel)
4. Run browser extraction (ThreadPoolExecutor)
   - Navigate to URL
   - Extract actions
   - Generate MCP JSON
   - Take screenshot
   - Generate preview HTML
   - ❌ browser_manager.close() called INSIDE context (BUG)
5. Save to KV store (await key_value_store.set_value())
6. Push to dataset (await Actor.push_data()) ← Must reach here
7. Actor completes
```

**If step 4 fails due to cleanup bug, step 6 never executes.**

## Next Steps

1. ✅ Fix browser cleanup (already done locally)
2. ⏳ Deploy fix to Apify
3. ⏳ Test with simple URL after deployment
4. ⏳ Verify dataset population
5. ⏳ Check if additional error handling needed

