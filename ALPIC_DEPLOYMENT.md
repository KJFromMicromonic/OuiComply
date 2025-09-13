# ALPIC Deployment Guide for OuiComply MCP Server

This guide provides step-by-step instructions for deploying the OuiComply MCP Server on ALPIC.

## 🚀 Quick Start

### Prerequisites

1. **ALPIC Account**: Ensure you have an active ALPIC account
2. **Mistral API Key**: Get your API key from [Mistral AI](https://console.mistral.ai/)
3. **Python 3.8+**: ALPIC supports Python 3.8 and higher

### Environment Variables

Set the following environment variables in your ALPIC dashboard:

```env
# Required
MISTRAL_KEY=your_mistral_api_key_here

# Optional - LeChat Memory Integration
LECHAT_API_URL=https://api.lechat.ai
LECHAT_API_KEY=your_lechat_api_key

# Optional - GitHub Integration
GITHUB_TOKEN=your_github_token
GITHUB_REPOSITORY=yourusername/your-repo

# ALPIC-specific
ALPIC_ENV=true
ENABLE_HEALTH_CHECK=true
HEALTH_CHECK_PATH=/health
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 📋 Build Settings

Configure your ALPIC build settings as follows:

### Install Command
```bash
uv sync --locked
```

### Start Command
```bash
python main.py
```

## 🏗️ Project Structure

Ensure your project has the following structure:

```
OuiComply/
├── main.py                 # Main entry point for ALPIC
├── health_check.py         # Health check endpoints
├── alpac.json             # ALPIC configuration
├── pyproject.toml         # Python project configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (local only)
├── src/
│   ├── mcp_server.py      # MCP server implementation
│   ├── config.py          # Configuration management
│   └── tools/             # Tool implementations
└── README.md
```

## 🔧 Configuration

### 1. ALPIC Configuration (alpac.json)

The `alpac.json` file contains ALPIC-specific configuration:

```json
{
  "name": "ouicomply-mcp",
  "version": "1.0.0",
  "main": "main.py",
  "environment": {
    "ALPIC_ENV": "true",
    "ENABLE_HEALTH_CHECK": "true",
    "HEALTH_CHECK_PATH": "/health"
  },
  "health_check": {
    "enabled": true,
    "path": "/health",
    "detailed_path": "/health/detailed"
  }
}
```

### 2. Python Dependencies

Dependencies are managed through `pyproject.toml` and `requirements.txt`:

- **pyproject.toml**: Main dependency management
- **requirements.txt**: Fallback for pip-based installation

### 3. Environment Variables

Set these in your ALPIC dashboard:

| Variable | Required | Description |
|----------|----------|-------------|
| `MISTRAL_KEY` | Yes | Mistral AI API key |
| `LECHAT_API_KEY` | No | LeChat memory integration |
| `GITHUB_TOKEN` | No | GitHub audit trail integration |
| `ALPIC_ENV` | Yes | Set to "true" for ALPIC |
| `ENABLE_HEALTH_CHECK` | No | Enable health check endpoint |
| `LOG_LEVEL` | No | Logging level (INFO, DEBUG, etc.) |

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository

1. Ensure all files are committed to your repository
2. Verify that `main.py` is in the root directory
3. Check that all dependencies are listed in `pyproject.toml`

### Step 2: Configure ALPIC

1. **Connect Repository**: Link your GitHub repository to ALPIC
2. **Set Environment Variables**: Add all required environment variables
3. **Configure Build Settings**:
   - Install Command: `uv sync --locked`
   - Start Command: `python main.py`

### Step 3: Deploy

1. **Trigger Deployment**: Push changes to your main branch
2. **Monitor Logs**: Check ALPIC logs for any startup issues
3. **Test Health Check**: Visit `/health` endpoint to verify deployment

## 🔍 Health Check Endpoints

### Basic Health Check
```
GET /health
```

Returns basic server status and configuration.

### Detailed Health Check
```
GET /health/detailed
```

Returns comprehensive health information including:
- Memory usage
- Disk space
- Network connectivity
- API endpoint status

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: Module import errors during startup
**Solution**: Ensure all imports use relative paths and `src/` is in Python path

#### 2. Missing Dependencies
**Problem**: Package installation failures
**Solution**: Check `pyproject.toml` and `requirements.txt` for all dependencies

#### 3. Configuration Errors
**Problem**: Server fails to start due to missing configuration
**Solution**: Verify all required environment variables are set in ALPIC dashboard

#### 4. Port Issues
**Problem**: Server can't bind to port
**Solution**: ALPIC automatically assigns ports via `PORT` environment variable

### Debug Mode

Enable debug logging by setting:
```env
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

### Local Testing

Test your deployment locally:
```bash
# Set ALPIC environment
export ALPIC_ENV=true
export PORT=3000

# Run the server
python main.py

# Test health check
curl http://localhost:3000/health
```

## 📊 Monitoring

### Logs
- ALPIC provides real-time logs in the dashboard
- Use structured logging (JSON format) for better parsing
- Set appropriate log levels for production

### Health Monitoring
- Use `/health` endpoint for basic monitoring
- Use `/health/detailed` for comprehensive health checks
- Set up alerts based on health check responses

### Performance
- Monitor memory usage through health checks
- Check response times for MCP tool calls
- Monitor API rate limits for Mistral AI

## 🔒 Security

### API Keys
- Store all API keys in ALPIC environment variables
- Never commit API keys to your repository
- Use different keys for development and production

### Network Security
- ALPIC handles HTTPS termination
- Use secure connections for external API calls
- Validate all inputs in MCP tools

## 📈 Scaling

### Resource Limits
- ALPIC provides configurable memory and CPU limits
- Monitor resource usage through health checks
- Adjust limits based on usage patterns

### Performance Optimization
- Use connection pooling for external APIs
- Implement caching for frequently accessed data
- Optimize document processing for large files

## 🆘 Support

### ALPIC Support
- Check ALPIC documentation for platform-specific issues
- Contact ALPIC support for deployment problems

### OuiComply Support
- Check logs for application-specific errors
- Review configuration settings
- Test locally before deploying

## 📚 Additional Resources

- [ALPIC Documentation](https://docs.alpic.com/)
- [Mistral AI Documentation](https://docs.mistral.ai/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [OuiComply GitHub Repository](https://github.com/yourusername/ouicomply)

---

**Note**: This deployment guide is specific to ALPIC. For other platforms, refer to the main README.md file.
