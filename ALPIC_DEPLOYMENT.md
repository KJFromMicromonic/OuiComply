# OuiComply MCP Server - Alpic Deployment Guide

This guide covers deploying the OuiComply MCP Server to Alpic, a platform specifically designed for MCP servers with excellent Python support.

## Why Alpic?

Alpic is purpose-built for MCP servers and offers:
- **Native MCP Support**: Built specifically for MCP protocol
- **Python SDK**: Full Python support without code changes
- **MCP Analytics**: Specialized monitoring for MCP servers
- **One-Click Deployment**: Simple GitHub integration
- **Managed Authentication**: Built-in OAuth and API key support
- **Transport Layer Abstraction**: Support for SSE, WebSockets, HTTP

## Prerequisites

1. **Alpic Account**: Sign up at [app.alpic.ai](https://app.alpic.ai)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Python MCP Server**: Your existing OuiComply MCP server

## Deployment Methods

### Method 1: GitHub Integration (Recommended)

1. **Sign Up and Connect GitHub**:
   - Go to [app.alpic.ai](https://app.alpic.ai)
   - Click "Sign in with GitHub"
   - Authorize Alpic AI to access your GitHub account

2. **Create Team and Project**:
   - Fill in your team name and click "Create team"
   - Click "New Project"
   - Add the Alpic AI app to your GitHub organization
   - Select the organization and repositories you want Alpic to access
   - Click "Install"

3. **Import Your Repository**:
   - Choose your OuiComply repository
   - Click "Import"

4. **Configure Project Settings**:
   - Choose the branch to sync (usually `main`)
   - Set environment variables:
     - `MISTRAL_API_KEY`: Your Mistral API key
     - `REDIS_URL`: Your Redis connection URL (optional)
   - Confirm build commands (auto-detected)
   - Click "Deploy" 🚀

### Method 2: Alpic CLI

1. **Install Alpic CLI**:
   ```bash
   npm install -g @alpic/cli
   ```

2. **Login to Alpic**:
   ```bash
   alpic login
   ```

3. **Initialize Project**:
   ```bash
   alpic init
   ```

4. **Set Environment Variables**:
   ```bash
   alpic env set MISTRAL_API_KEY=your_mistral_api_key_here
   alpic env set REDIS_URL=your_redis_url_here
   ```

5. **Deploy**:
   ```bash
   alpic deploy
   ```

## Configuration Files

### alpic.yaml
```yaml
name: ouicomply-mcp-server
version: 1.0.0
description: "OuiComply MCP Server - AI Assisted Legal Compliance Checker"

build:
  command: "pip install -r requirements.txt"
  python_version: "3.12"

runtime:
  command: "python start_fastmcp_server.py"
  port: 8000
  health_check: "/health"

environment:
  MISTRAL_API_KEY: "${MISTRAL_API_KEY}"
  REDIS_URL: "${REDIS_URL}"
  PORT: "8000"
  HOST: "0.0.0.0"

mcp:
  server_name: "ouicomply-mcp"
  server_version: "1.0.0"
  capabilities:
    tools: true
    resources: true
    prompts: false
    logging: true
```

### .alpicignore
```
__pycache__/
*.py[cod]
venv/
env/
.git/
*.md
test_*.py
*.log
```

## Environment Variables

Set these in the Alpic dashboard:

| Variable | Description | Required |
|----------|-------------|----------|
| `MISTRAL_API_KEY` | Your Mistral API key for AI analysis | Yes |
| `REDIS_URL` | Redis connection URL for caching | No |
| `PORT` | Port number (Alpic sets this automatically) | No |
| `HOST` | Host address (defaults to 0.0.0.0) | No |

## MCP-Specific Features

### MCP Analytics
Alpic provides specialized analytics for MCP servers:
- Tool usage statistics
- Resource access patterns
- Performance metrics
- Error tracking
- User behavior insights

### Authentication
Secure your MCP server with:
- OAuth integration
- API key authentication
- Dynamic Client Registration
- Rate limiting

### Custom Domains
Use your own domain:
- Configure custom domain in Alpic dashboard
- SSL certificates managed automatically
- Professional branding

## Testing Your Deployment

### Health Check
The server runs a separate health check server on port 8001. Test it with:
```bash
curl https://your-app.alpic.ai:8001/health
```

Or if the health check is configured to use the main port:
```bash
curl https://your-app.alpic.ai/health
```

### MCP Tools Testing
```bash
# Test analyze_document tool
curl -X POST https://your-app.alpic.ai/mcp/analyze_document \
  -H "Content-Type: application/json" \
  -d '{
    "document_content": "Your document text here",
    "document_type": "contract",
    "frameworks": ["gdpr", "sox"]
  }'
```

### MCP Inspector
Use Alpic's MCP Inspector to test your server:
1. Go to your project dashboard
2. Click "MCP Inspector"
3. Test all tools and resources
4. View real-time logs

## Monitoring and Management

### Analytics Dashboard
- View MCP-specific metrics
- Monitor tool usage
- Track performance
- Analyze user behavior

### Logs
- Real-time log streaming
- Log retention (30 days)
- Error tracking
- Performance monitoring

### Scaling
- Automatic scaling based on demand
- Manual scaling options
- Resource monitoring
- Cost optimization

## Advanced Features

### Multiple Environments
- Production environment
- Staging environment
- Development environment
- Environment-specific configurations

### CI/CD Integration
- GitHub Actions integration
- Automatic deployments
- Branch-based deployments
- Rollback capabilities

### Security
- Built-in rate limiting
- DDoS protection
- Code analysis
- Compliance monitoring

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check `requirements.txt` for all dependencies
   - Verify Python version compatibility
   - Check build logs in Alpic dashboard

2. **Runtime Errors**:
   - Verify environment variables are set
   - Check application logs
   - Ensure health check endpoint works

3. **MCP Protocol Issues**:
   - Use MCP Inspector to test protocol compliance
   - Check tool and resource definitions
   - Verify response formats

### Debug Commands

```bash
# Check deployment status
alpic status

# View logs
alpic logs

# Test MCP server
alpic test

# Get deployment info
alpic info
```

## Production Readiness

### Security Checklist
- [ ] Environment variables secured
- [ ] Authentication enabled (if needed)
- [ ] Rate limiting configured
- [ ] CORS properly configured

### Performance Checklist
- [ ] Health check responds quickly
- [ ] MCP tools perform within SLA
- [ ] Monitoring and alerting set up
- [ ] Scaling configured appropriately

### Reliability Checklist
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Backup and recovery procedures
- [ ] Monitoring and alerting active

## Next Steps

After successful deployment:

1. **Test Thoroughly**:
   - Use MCP Inspector to test all functionality
   - Verify all tools and resources work correctly
   - Test with real MCP clients

2. **Set Up Monitoring**:
   - Configure alerts for critical metrics
   - Set up log monitoring
   - Enable MCP Analytics

3. **Configure Security**:
   - Enable authentication if needed
   - Set up rate limiting
   - Configure CORS properly

4. **Optimize Performance**:
   - Monitor resource usage
   - Optimize tool responses
   - Configure scaling policies

5. **Distribute to Users**:
   - Share your MCP server URL
   - Provide integration documentation
   - Set up user support

## Support

- **Alpic Documentation**: [docs.alpic.ai](https://docs.alpic.ai)
- **Alpic Discord**: Join the community Discord
- **Alpic Support**: Contact support through the dashboard
- **OuiComply Issues**: Create an issue in your repository

---

**Deployment URL**: `https://your-app.alpic.ai`
**Health Check**: `https://your-app.alpic.ai/health`
**MCP Endpoint**: `https://your-app.alpic.ai/mcp/`

**Note**: Alpic is specifically designed for MCP servers, so your deployment will be optimized for MCP protocol compliance and performance.
