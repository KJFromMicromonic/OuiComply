# OuiComply MCP Server - Deployment Checklist

## Choose Your Deployment Platform

- **Railway**: General Python hosting with good MCP support
- **Alpic**: Purpose-built for MCP servers with specialized features

## Railway Deployment Checklist

## Pre-Deployment Checklist

### ✅ Code Preparation
- [x] All Python dependencies listed in `requirements.txt`
- [x] Python version specified in `runtime.txt` (3.12.0)
- [x] Railway configuration files created:
  - [x] `railway.toml`
  - [x] `Procfile`
- [x] Health check server created (`health_server.py`)
- [x] Port configuration updated to use `os.environ.get("PORT")`
- [x] Start script updated for Railway deployment

### ✅ Environment Variables
- [ ] `MISTRAL_API_KEY` - Your Mistral API key
- [ ] `REDIS_URL` - Redis connection URL (optional)
- [ ] `PORT` - Automatically set by Railway
- [ ] `HOST` - Automatically set by Railway

### ✅ Testing
- [ ] Test server locally with `python start_fastmcp_server.py`
- [ ] Verify health check endpoint works: `curl http://localhost:8001/health`
- [ ] Test MCP tools and resources locally
- [ ] Verify all imports work correctly

## Deployment Steps

### Option 1: Railway CLI
1. [ ] Install Railway CLI: `npm install -g @railway/cli`
2. [ ] Login: `railway login`
3. [ ] Initialize project: `railway init`
4. [ ] Set environment variables:
   ```bash
   railway variables set MISTRAL_API_KEY=your_key_here
   railway variables set REDIS_URL=your_redis_url_here
   ```
5. [ ] Deploy: `railway up`

### Option 2: GitHub Integration
1. [ ] Push code to GitHub repository
2. [ ] Go to [railway.app](https://railway.app)
3. [ ] Create new project
4. [ ] Connect GitHub repository
5. [ ] Set environment variables in Railway dashboard
6. [ ] Deploy automatically

## Post-Deployment Verification

### ✅ Health Check
- [ ] Verify health endpoint: `curl https://your-app.railway.app:8001/health`
- [ ] Check response includes status: "healthy"

### ✅ MCP Tools Testing
- [ ] Test `analyze_document` tool
- [ ] Test `update_memory` tool
- [ ] Test `get_compliance_status` tool
- [ ] Test `automate_compliance_workflow` tool

### ✅ MCP Resources Testing
- [ ] Test `compliance_frameworks` resource
- [ ] Test `legal_templates` resource
- [ ] Test `team_memory` resource

### ✅ Monitoring Setup
- [ ] Check Railway dashboard for deployment status
- [ ] Monitor logs: `railway logs`
- [ ] Set up alerts if needed

## Production Readiness

### ✅ Security
- [ ] Environment variables are secure
- [ ] No sensitive data in code
- [ ] HTTPS is enabled (Railway default)

### ✅ Performance
- [ ] Health check responds quickly
- [ ] MCP tools respond within acceptable time
- [ ] Memory usage is reasonable

### ✅ Reliability
- [ ] Server restarts successfully
- [ ] Error handling works correctly
- [ ] Logs are properly formatted

## Troubleshooting

### Common Issues
- **Port binding errors**: Ensure using `os.environ.get("PORT")`
- **Import errors**: Check all dependencies in `requirements.txt`
- **Environment variable issues**: Verify variables are set in Railway
- **Health check failures**: Check `/health` endpoint implementation

### Debug Commands
```bash
# Check deployment status
railway status

# View logs
railway logs --follow

# Connect to container
railway shell
```

## Next Steps After Deployment

1. [ ] Update documentation with production URL
2. [ ] Set up monitoring and alerting
3. [ ] Configure custom domain (optional)
4. [ ] Set up CI/CD for automatic deployments
5. [ ] Implement proper logging and error handling
6. [ ] Test with real MCP clients

---

**Deployment URL**: `https://your-app-name.railway.app`
**Health Check**: `https://your-app-name.railway.app:8001/health`
**MCP Endpoint**: `https://your-app-name.railway.app/mcp/`

## Alpic Deployment Checklist

### Pre-Deployment Checklist

#### ✅ Code Preparation
- [x] All Python dependencies listed in `requirements.txt`
- [x] Python version specified in `runtime.txt` (3.12.0)
- [x] Alpic configuration files created:
  - [x] `alpic.yaml`
  - [x] `.alpicignore`
- [x] Health check server created (`health_server.py`)
- [x] Port configuration updated to use `os.environ.get("PORT")`
- [x] Start script updated for Alpic deployment

#### ✅ Environment Variables
- [ ] `MISTRAL_API_KEY` - Your Mistral API key
- [ ] `REDIS_URL` - Redis connection URL (optional)
- [ ] `PORT` - Automatically set by Alpic
- [ ] `HOST` - Automatically set by Alpic

#### ✅ Testing
- [ ] Test server locally with `python start_fastmcp_server.py`
- [ ] Verify health check endpoint works: `curl http://localhost:8001/health`
- [ ] Test MCP tools and resources locally
- [ ] Verify all imports work correctly

### Deployment Steps

#### Option 1: GitHub Integration (Recommended)
1. [ ] Sign up at [app.alpic.ai](https://app.alpic.ai)
2. [ ] Connect GitHub account
3. [ ] Create team and project
4. [ ] Import OuiComply repository
5. [ ] Configure environment variables in Alpic dashboard
6. [ ] Deploy automatically

#### Option 2: Alpic CLI
1. [ ] Install Alpic CLI: `npm install -g @alpic/cli`
2. [ ] Login: `alpic login`
3. [ ] Initialize project: `alpic init`
4. [ ] Set environment variables:
   ```bash
   alpic env set MISTRAL_API_KEY=your_key_here
   alpic env set REDIS_URL=your_redis_url_here
   ```
5. [ ] Deploy: `alpic deploy`

### Post-Deployment Verification

#### ✅ Health Check
- [ ] Verify health endpoint: `curl https://your-app.alpic.ai:8001/health`
- [ ] Check response includes status: "healthy"

#### ✅ MCP Tools Testing
- [ ] Test `analyze_document` tool
- [ ] Test `update_memory` tool
- [ ] Test `get_compliance_status` tool
- [ ] Test `automate_compliance_workflow` tool

#### ✅ MCP Resources Testing
- [ ] Test `compliance_frameworks` resource
- [ ] Test `legal_templates` resource
- [ ] Test `team_memory` resource

#### ✅ MCP Inspector Testing
- [ ] Use Alpic's MCP Inspector to test all functionality
- [ ] Verify MCP protocol compliance
- [ ] Test with real MCP clients

#### ✅ Monitoring Setup
- [ ] Check Alpic dashboard for deployment status
- [ ] Enable MCP Analytics
- [ ] Set up monitoring and alerting
- [ ] Configure authentication if needed

### Production Readiness

#### ✅ Security
- [ ] Environment variables are secure
- [ ] Authentication configured (if needed)
- [ ] Rate limiting enabled
- [ ] CORS properly configured

#### ✅ Performance
- [ ] Health check responds quickly
- [ ] MCP tools respond within acceptable time
- [ ] MCP Analytics enabled
- [ ] Scaling configured appropriately

#### ✅ Reliability
- [ ] Server restarts successfully
- [ ] Error handling works correctly
- [ ] Logs are properly formatted
- [ ] Monitoring and alerting active

## Support

### Railway
- Railway Documentation: [docs.railway.com](https://docs.railway.com)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)

### Alpic
- Alpic Documentation: [docs.alpic.ai](https://docs.alpic.ai)
- Alpic Discord: Join the community Discord

### General
- OuiComply Issues: Create an issue in your repository
