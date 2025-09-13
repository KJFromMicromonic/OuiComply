# Deploy OuiComply MCP Server to Cloud

## 🚀 Quick Deployment Options

Since ngrok is having certificate issues, here are the best ways to deploy your MCP Server to the cloud for Le Chat integration.

## Option 1: Railway (Recommended - Easiest)

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Create Railway Project
```bash
# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 3. Configure Environment
Railway will automatically detect your Python app and deploy it. The server will be available at a public URL like `https://your-app.railway.app`

## Option 2: Render (Free Tier Available)

### 1. Create render.yaml
```yaml
services:
  - type: web
    name: ouicomply-mcp
    env: python
    buildCommand: pip install -r requirements_fastapi.txt
    startCommand: python fastapi_simple.py
    envVars:
      - key: PORT
        value: 8000
```

### 2. Deploy via GitHub
1. Push your code to GitHub
2. Connect repository to Render
3. Deploy automatically

## Option 3: Heroku

### 1. Create Procfile
```bash
echo "web: python fastapi_simple.py" > Procfile
```

### 2. Create requirements.txt
```bash
# Copy from requirements_fastapi.txt
cp requirements_fastapi.txt requirements.txt
```

### 3. Deploy
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create ouicomply-mcp

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

## Option 4: Vercel (Serverless)

### 1. Create vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "fastapi_simple.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "fastapi_simple.py"
    }
  ]
}
```

### 2. Deploy
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

## 🔧 Update Server for Cloud Deployment

### Modify fastapi_simple.py for Cloud
```python
# Update the uvicorn.run section at the bottom:
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "fastapi_simple:app",
        host="0.0.0.0",  # Important: Use 0.0.0.0 for cloud
        port=port,
        reload=False
    )
```

## 📋 Environment Variables

Set these in your cloud service:

- `PORT`: 8000 (or let the service assign it)
- `MISTRAL_API_KEY`: Your Mistral API key (if using real API calls)

## 🧪 Test Your Deployment

Once deployed, test your cloud deployment:

```bash
# Replace YOUR_URL with your actual deployment URL
curl https://YOUR_URL/health
curl https://YOUR_URL/lechat/integration
```

## 🔗 Configure Le Chat

Once you have a public URL:

1. **Add MCP Server in Le Chat**:
   - URL: `https://your-deployment-url.com`
   - Name: `OuiComply MCP Server`

2. **Test Integration**:
   - Use the `/lechat/test` endpoint
   - Send document analysis requests
   - Verify memory integration is working

## 🎯 Recommended Approach

1. **For Quick Testing**: Use Railway (easiest setup)
2. **For Production**: Use Render or Heroku (more stable)
3. **For Development**: Use local testing with the HTML interface

## 📞 Support

If you need help with deployment:

1. Check the cloud service documentation
2. Verify your `requirements_fastapi.txt` has all dependencies
3. Ensure your server uses `host="0.0.0.0"` for cloud deployment
4. Test locally first with `python test_lechat_integration.py`

---

**Status**: ✅ Ready for Cloud Deployment
**Local Testing**: ✅ Working
**Cloud Options**: ✅ Multiple options available
**Le Chat Integration**: ✅ Ready once deployed
