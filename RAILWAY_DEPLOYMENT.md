# OuiComply MCP Server - Railway Deployment Guide

This guide covers deploying the OuiComply MCP Server to Railway, a platform that supports Python applications without requiring code changes.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install the Railway CLI
   ```bash
   npm install -g @railway/cli
   ```
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Deployment Methods

### Method 1: Railway CLI (Recommended)

1. **Login to Railway**:
   ```bash
   railway login
   ```

2. **Initialize Railway in your project**:
   ```bash
   railway init
   ```

3. **Set Environment Variables**:
   ```bash
   railway variables set MISTRAL_API_KEY=your_mistral_api_key_here
   railway variables set REDIS_URL=your_redis_url_here
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

### Method 2: GitHub Integration

1. **Connect GitHub Repository**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your OuiComply repository

2. **Configure Environment Variables**:
   - In the Railway dashboard, go to your project
   - Navigate to "Variables" tab
   - Add the following variables:
     - `MISTRAL_API_KEY`: Your Mistral API key
     - `REDIS_URL`: Your Redis connection URL (optional)

3. **Deploy**:
   - Railway will automatically detect your Python application
   - It will build and deploy using the `requirements.txt` file
   - The deployment will use the `Procfile` to start the server

## Configuration Files

### railway.toml
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python start_fastmcp_server.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"

[env]
PORT = "8000"
```

### Procfile
```
web: python start_fastmcp_server.py
```

### runtime.txt
```
python-3.12.0
```

## Environment Variables

Set these environment variables in Railway:

| Variable | Description | Required |
|----------|-------------|----------|
| `MISTRAL_API_KEY` | Your Mistral API key for AI analysis | Yes |
| `REDIS_URL` | Redis connection URL for caching | No |
| `PORT` | Port number (Railway sets this automatically) | No |
| `HOST` | Host address (defaults to 0.0.0.0) | No |

## Health Check

The server includes a separate health check server running on port 8001 that provides a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "service": "OuiComply MCP Server",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## MCP Client Integration

Once deployed, your MCP server will be available at:
```
https://your-app-name.railway.app
```

### Available Endpoints

- **Tools** (POST `/mcp/{tool_name}`):
  - `analyze_document`: AI-powered document compliance analysis
  - `update_memory`: Store team compliance insights
  - `get_compliance_status`: Get team compliance status
  - `automate_compliance_workflow`: Automate compliance workflows

- **Resources** (GET `/mcp/resources/{resource_name}`):
  - `compliance_frameworks`: Get compliance framework definitions
  - `legal_templates`: Get legal document templates
  - `team_memory`: Get team memory and insights

### Example Usage

```bash
# Health check
curl https://your-app-name.railway.app/health

# Analyze document
curl -X POST https://your-app-name.railway.app/mcp/analyze_document \
  -H "Content-Type: application/json" \
  -d '{
    "document_content": "Your document text here",
    "document_type": "contract",
    "frameworks": ["gdpr", "sox"]
  }'
```

## Monitoring and Logs

1. **View Logs**:
   ```bash
   railway logs
   ```

2. **Monitor in Dashboard**:
   - Go to your project in Railway dashboard
   - Click on "Deployments" to see deployment history
   - Click on "Logs" to view real-time logs

## Troubleshooting

### Common Issues

1. **Port Configuration**:
   - Ensure your app uses `os.environ.get("PORT", 8000)` for the port
   - Railway automatically sets the PORT environment variable

2. **Dependencies**:
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version is specified in `runtime.txt`

3. **Environment Variables**:
   - Verify all required environment variables are set
   - Check that API keys are valid

4. **Health Check**:
   - Ensure the `/health` endpoint returns a 200 status
   - Check that the endpoint is accessible

### Debug Commands

```bash
# Check deployment status
railway status

# View detailed logs
railway logs --follow

# Connect to running container (if needed)
railway shell
```

## Scaling

Railway automatically handles scaling based on traffic. For manual scaling:

1. Go to your project dashboard
2. Navigate to "Settings" > "Scaling"
3. Adjust CPU and memory limits as needed

## Security Considerations

1. **Environment Variables**: Never commit API keys to your repository
2. **HTTPS**: Railway provides HTTPS by default
3. **Rate Limiting**: Consider implementing rate limiting for production use
4. **Authentication**: Add authentication if exposing the server publicly

## Support

- **Railway Documentation**: [docs.railway.com](https://docs.railway.com)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **OuiComply Issues**: Create an issue in your repository

## Next Steps

After successful deployment:

1. Test all MCP tools and resources
2. Set up monitoring and alerting
3. Configure custom domain (optional)
4. Set up CI/CD for automatic deployments
5. Implement proper logging and error handling

---

**Note**: This deployment maintains your existing Python codebase and structure. No code changes are required beyond the configuration files provided.
