# Vercel Deployment Guide for OuiComply MCP Server

This guide explains how to deploy the OuiComply MCP Server to Vercel for Le Chat integration.

## 🚀 Quick Deployment

### Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Environment Variables**: Set up your API keys

### Step 1: Prepare Your Repository

Ensure your repository contains:
- `vercel.json` - Vercel configuration
- `api/mcp.py` - Main MCP server API route
- `api/health.py` - Health check endpoint
- `requirements.txt` - Python dependencies
- `src/` directory with your tools

### Step 2: Deploy to Vercel

1. **Connect Repository**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project**:
   - Framework Preset: `Other`
   - Root Directory: `./` (or leave empty)
   - Build Command: Leave empty (Vercel will auto-detect)
   - Output Directory: Leave empty

3. **Set Environment Variables**:
   - Go to Project Settings → Environment Variables
   - Add the following variables:
     ```
     MISTRAL_API_KEY=your_mistral_api_key
     LECHAT_API_KEY=your_lechat_api_key (optional)
     LOG_LEVEL=INFO
     ```

4. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete

### Step 3: Test Your Deployment

1. **Get Your Deployment URL**:
   - After deployment, you'll get a URL like `https://your-app.vercel.app`

2. **Test the Health Check**:
   ```bash
   curl https://your-app.vercel.app/health
   ```

3. **Test MCP Protocol**:
   ```bash
   curl -X POST https://your-app.vercel.app/mcp \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "initialize",
       "params": {
         "protocolVersion": "2024-11-05",
         "capabilities": {
           "tools": {"listChanged": true},
           "resources": {"subscribe": true, "listChanged": true},
           "prompts": {"listChanged": true}
         }
       }
     }'
   ```

4. **Run Automated Tests**:
   ```bash
   python test_vercel_deployment.py
   ```

## 🔧 Configuration

### Vercel Configuration (`vercel.json`)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/mcp.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/mcp",
      "dest": "/api/mcp"
    },
    {
      "src": "/health",
      "dest": "/api/health"
    },
    {
      "src": "/",
      "dest": "/api/health"
    }
  ],
  "env": {
    "PYTHONPATH": "."
  }
}
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MISTRAL_API_KEY` | Your Mistral API key | Yes |
| `LECHAT_API_KEY` | Le Chat API key (optional) | No |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | No |

## 📡 API Endpoints

### Health Check
- **URL**: `GET /health`
- **Description**: Check server health and status
- **Response**: JSON with server status and capabilities

### MCP Protocol
- **URL**: `POST /mcp`
- **Description**: Main MCP protocol endpoint
- **Content-Type**: `application/json`
- **Methods Supported**:
  - `initialize` - Initialize MCP connection
  - `tools/list` - List available tools
  - `tools/call` - Call a tool
  - `resources/list` - List available resources
  - `resources/read` - Read a resource
  - `prompts/list` - List available prompts
  - `prompts/get` - Get a prompt

## 🛠️ Available Tools

1. **analyze_document**
   - Analyzes documents for compliance issues
   - Parameters: `document_content`, `document_type`, `frameworks`

2. **update_memory**
   - Updates team memory with insights
   - Parameters: `team_id`, `insight`, `category`

3. **get_compliance_status**
   - Gets team compliance status
   - Parameters: `team_id`, `framework`

## 🔗 Le Chat Integration

To integrate with Le Chat:

1. **Get Your MCP Server URL**:
   ```
   https://your-app.vercel.app/mcp
   ```

2. **Configure Le Chat**:
   - Add the MCP server URL to your Le Chat configuration
   - The server supports the standard MCP protocol

3. **Test Integration**:
   - Use the test script to verify everything works
   - Check Le Chat logs for any connection issues

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure all dependencies are in `requirements.txt`
   - Check that `src/` directory is properly included

2. **Timeout Errors**:
   - Vercel has a 10-second timeout for serverless functions
   - Consider optimizing long-running operations

3. **Memory Issues**:
   - Vercel has memory limits for serverless functions
   - Monitor memory usage in your tools

4. **CORS Issues**:
   - The server includes CORS headers
   - If you still have issues, check your client configuration

### Debugging

1. **Check Vercel Logs**:
   - Go to your project dashboard
   - Click on "Functions" tab
   - View logs for debugging

2. **Test Locally**:
   - Use `vercel dev` to test locally
   - This helps debug issues before deployment

3. **Health Check**:
   - Always test `/health` endpoint first
   - This verifies basic connectivity

## 📊 Monitoring

### Vercel Analytics
- Monitor function invocations
- Check response times
- Track error rates

### Custom Monitoring
- Add logging to your tools
- Monitor API usage
- Track compliance analysis metrics

## 🔄 Updates and Maintenance

### Updating the Server
1. Push changes to your GitHub repository
2. Vercel will automatically redeploy
3. Test the new deployment

### Environment Variables
- Update environment variables in Vercel dashboard
- Redeploy after changes

### Dependencies
- Update `requirements.txt` for new dependencies
- Vercel will install new packages on next deployment

## 🎉 Success!

Once deployed, your MCP server will be available at:
- **MCP Endpoint**: `https://your-app.vercel.app/mcp`
- **Health Check**: `https://your-app.vercel.app/health`

You can now integrate this with Le Chat or any other MCP-compatible client!
