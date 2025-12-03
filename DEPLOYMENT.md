# 🚀 Deployment Guide - MCP Website Tool Actor

## ✅ Bug Fix Applied

**Root Cause:** The actor was missing critical configuration files:
- ❌ No `apify.json` (had `apify.json.deprecated`)
- ❌ No `Dockerfile` to specify the entry point
- ❌ No `requirements.txt` as fallback

**Result:** Apify didn't know what script to run, so it completed successfully but did nothing (0 results).

## 📁 Files Created

1. **`apify.json`** - Actor configuration with proper storages
2. **`Dockerfile`** - Python 3.11 + Playwright setup
3. **`requirements.txt`** - Dependencies list
4. **`.dockerignore`** - Exclude test files from Docker build

## 🧪 Test Locally (Optional)

Before deploying, you can test locally:

```bash
cd "F:\AI Projects\mcp-website-tool"
python test_local.py
```

This will run the actor with mock Apify SDK and verify data is pushed.

## 📤 Deploy to Apify

### Option 1: Via Apify CLI (Recommended)

```bash
# Install Apify CLI if not installed
npm install -g apify-cli

# Login to Apify
apify login

# Navigate to project
cd "F:\AI Projects\mcp-website-tool"

# Push to Apify
apify push
```

### Option 2: Via Apify Console

1. Go to https://console.apify.com/actors
2. Click "Create new" → "From GitHub" or "Import from ZIP"
3. Upload your actor or connect GitHub repo
4. Apify will build using the `Dockerfile`

### Option 3: Manual Build

If you have issues, you can manually build:

```bash
# Navigate to project
cd "F:\AI Projects\mcp-website-tool"

# Build locally
docker build -t mcp-website-tool .

# Test the Docker image
docker run -e APIFY_TOKEN=your_token_here mcp-website-tool
```

## ✅ Verify Deployment

After deploying, test the actor:

1. Go to https://console.apify.com/actors/clever_fashion~mcp-website-tool
2. Click "Try it"
3. Enter input:
   ```json
   {
     "url": "https://example.com"
   }
   ```
4. Click "Start"
5. **Check Results:**
   - Should find interactive elements (buttons, inputs, forms)
   - Should push data to dataset with `mcpJsonUrl`, `previewUrl`, `screenshotUrl`
   - Dataset should NO LONGER be empty!

## 🔍 Expected Output

The actor should now return:

```json
{
  "mcpJsonUrl": "https://api.apify.com/v2/key-value-stores/.../mcp-xxx.json",
  "previewUrl": "https://api.apify.com/v2/key-value-stores/.../preview-xxx.html",
  "screenshotUrl": "https://api.apify.com/v2/key-value-stores/.../screenshot-xxx.png",
  "toolCount": 5,
  "url": "https://example.com",
  "runId": "abc123",
  "actionsCount": 5
}
```

## 🐛 Troubleshooting

### If dataset is still empty:

1. **Check logs:** Look for errors in the Apify console
2. **Check entry point:** Verify `Dockerfile` CMD is correct
3. **Check dependencies:** Ensure all packages install correctly
4. **Test locally:** Run `test_local.py` to isolate issues

### If build fails:

1. **Check Dockerfile:** Ensure base image is correct (`apify/actor-python-playwright:3.11`)
2. **Check dependencies:** Verify `pyproject.toml` and `requirements.txt` are valid
3. **Check Playwright:** Ensure browsers install correctly

## 📊 Integration with Next.js App

Once deployed and working, your Next.js MCP.tools app at `F:\AI Projects\mcp-tools` will:

1. ✅ Call `/api/generate` endpoint
2. ✅ Start Apify actor with URL
3. ✅ Actor extracts elements and generates MCP tools
4. ✅ Returns `mcpJsonUrl` and `previewUrl`
5. ✅ Redirects to `/success` page with download links
6. ✅ Users can one-click import to Cursor/Claude!

## 🎉 Success Criteria

- ✅ Actor builds without errors
- ✅ Actor runs and completes (status: SUCCEEDED)
- ✅ Dataset has 1 entry (not 0!)
- ✅ Entry contains `mcpJsonUrl`, `previewUrl`, `screenshotUrl`
- ✅ Next.js app successfully shows success page

---

**Questions?** Check the Apify documentation: https://docs.apify.com/

