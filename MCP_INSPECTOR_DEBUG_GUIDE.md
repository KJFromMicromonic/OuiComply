# MCP Inspector Debug Guide for OuiComply

This guide provides comprehensive instructions for debugging OuiComply MCP servers using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

## 🚀 Quick Start

### 1. Install MCP Inspector

```bash
npm install -g @modelcontextprotocol/inspector
```

### 2. Check Dependencies

```bash
python debug_with_inspector.py --check
```

### 3. Launch Inspector

```bash
# Start with standard server
python debug_with_inspector.py --server standard --inspector

# Or use Windows batch script
debug_mcp.bat inspector standard

# Or use PowerShell
.\debug_mcp.ps1 inspector standard
```

## 📋 Available Servers

| Server Name | Type | Description | Command |
|-------------|------|-------------|---------|
| `ouicomply-standard` | stdio | Full MCP server with all tools | `python mcp_server.py` |
| `ouicomply-fastmcp` | stdio | FastMCP implementation | `python mcp_fastmcp_server.py` |
| `ouicomply-alpic` | stdio | ALPIC-optimized server | `python alpic_fastmcp_server.py` |
| `ouicomply-vercel` | http | Vercel serverless deployment | `https://your-app.vercel.app/mcp` |
| `ouicomply-local-http` | http | Local HTTP server | `http://localhost:3000/mcp` |
| `ouicomply-sse` | sse | Server-Sent Events | `http://localhost:3000/sse` |

## 🔧 Debug Commands

### Python Script Commands

```bash
# Check all dependencies
python debug_with_inspector.py --check

# List available servers
python debug_with_inspector.py --list

# Start a specific server
python debug_with_inspector.py --server standard
python debug_with_inspector.py --server fastmcp
python debug_with_inspector.py --server alpic

# Start server with inspector
python debug_with_inspector.py --server standard --inspector

# Test server via CLI
python debug_with_inspector.py --test standard --method tools/list
python debug_with_inspector.py --test fastmcp --method resources/list
```

### Windows Batch Commands

```cmd
# Check dependencies
debug_mcp.bat check

# List servers
debug_mcp.bat list

# Start servers
debug_mcp.bat standard
debug_mcp.bat fastmcp
debug_mcp.bat alpic

# Launch inspector
debug_mcp.bat inspector standard
debug_mcp.bat inspector fastmcp

# Test servers
debug_mcp.bat test standard tools/list
debug_mcp.bat test fastmcp resources/list
```

### PowerShell Commands

```powershell
# Check dependencies
.\debug_mcp.ps1 check

# List servers
.\debug_mcp.ps1 list

# Start servers
.\debug_mcp.ps1 standard
.\debug_mcp.ps1 fastmcp
.\debug_mcp.ps1 alpic

# Launch inspector
.\debug_mcp.ps1 inspector standard
.\debug_mcp.ps1 inspector fastmcp

# Test servers
.\debug_mcp.ps1 test standard tools/list
.\debug_mcp.ps1 test fastmcp resources/list
```

## 🌐 Web Interface

Once the inspector is running, access it at:
- **URL**: `http://localhost:6274`
- **Features**:
  - Visual tool testing with forms
  - Resource browser
  - Request/response logging
  - Error debugging
  - Real-time monitoring

## 🛠️ Configuration

### MCP Inspector Config (`mcp-inspector-config.json`)

```json
{
  "mcpServers": {
    "ouicomply-standard": {
      "type": "stdio",
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "PYTHONPATH": ".",
        "MISTRAL_KEY": "${MISTRAL_KEY}",
        "LECHAT_API_KEY": "${LECHAT_API_KEY}",
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "LOG_LEVEL": "INFO"
      }
    }
  },
  "settings": {
    "MCP_SERVER_REQUEST_TIMEOUT": 30000,
    "MCP_REQUEST_TIMEOUT_RESET_ON_PROGRESS": true,
    "MCP_PROXY_FULL_ADDRESS": "http://localhost:6274",
    "MCP_SERVER_LOG_LEVEL": "debug"
  }
}
```

### Environment Variables

Set these environment variables for full functionality:

```bash
# Required
export MISTRAL_KEY="your_mistral_api_key_here"

# Optional - LeChat Memory Integration
export LECHAT_API_KEY="your_lechat_api_key"

# Optional - GitHub Integration
export GITHUB_TOKEN="your_github_token"

# Optional - Server Configuration
export LOG_LEVEL="INFO"
export ALPIC_ENV="true"
```

## 🧪 Testing Workflows

### 1. Basic Server Test

```bash
# Start server
python debug_with_inspector.py --server standard

# In another terminal, test tools
python debug_with_inspector.py --test standard --method tools/list
```

### 2. Visual Debugging

```bash
# Start server with inspector
python debug_with_inspector.py --server standard --inspector

# Open browser to http://localhost:6274
# Use the web interface to test tools interactively
```

### 3. CLI Testing

```bash
# Test specific MCP methods
python debug_with_inspector.py --test standard --method tools/list
python debug_with_inspector.py --test standard --method resources/list
python debug_with_inspector.py --test standard --method prompts/list
```

### 4. HTTP Server Testing

```bash
# Start HTTP server
python debug_with_inspector.py --server alpic --port 3000

# Test HTTP endpoint
curl http://localhost:3000/health
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

## 🔍 Debugging Tools

### Available MCP Tools

1. **`analyze_document`**: Analyze documents for compliance
2. **`update_memory`**: Update team memory with insights
3. **`get_compliance_status`**: Get team compliance status
4. **`automate_compliance_workflow`**: Automate compliance workflows

### Available Resources

1. **`resource://compliance-frameworks`**: Supported compliance frameworks
2. **`resource://legal-templates`**: Legal document templates
3. **`resource://team-memory`**: Team-specific compliance insights

### Available Prompts

1. **`compliance_analysis`**: Generate compliance analysis prompts

## 🚨 Troubleshooting

### Common Issues

#### 1. MCP Inspector Not Found

**Error**: `❌ MCP Inspector not found`

**Solution**:
```bash
npm install -g @modelcontextprotocol/inspector
```

#### 2. Python Dependencies Missing

**Error**: `❌ Some dependencies are missing`

**Solution**:
```bash
pip install -r requirements.txt
```

#### 3. Server Won't Start

**Error**: Server process exits immediately

**Solutions**:
- Check environment variables: `echo $MISTRAL_KEY`
- Verify Python path: `which python`
- Check server logs for specific errors
- Ensure all dependencies are installed

#### 4. Inspector Can't Connect

**Error**: Inspector shows connection errors

**Solutions**:
- Ensure server is running before launching inspector
- Check configuration file paths
- Verify server name matches configuration
- Check for port conflicts

#### 5. Permission Errors (Windows)

**Error**: `Access is denied` or similar

**Solutions**:
- Run PowerShell as Administrator
- Check file permissions
- Use `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Debug Logs

Enable debug logging:

```bash
export LOG_LEVEL="DEBUG"
python debug_with_inspector.py --server standard --inspector
```

### Server Logs

Check server output for errors:

```bash
# Start server in foreground to see logs
python mcp_server.py

# Or check background process logs
python debug_with_inspector.py --server standard
```

## 📊 Performance Testing

### Load Testing

```bash
# Test multiple concurrent requests
for i in {1..10}; do
  python debug_with_inspector.py --test standard --method tools/list &
done
wait
```

### Memory Testing

```bash
# Monitor memory usage
python -c "
import psutil
import time
while True:
    print(f'Memory: {psutil.virtual_memory().percent}%')
    time.sleep(1)
"
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: MCP Server Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm install -g @modelcontextprotocol/inspector
      - run: pip install -r requirements.txt
      - run: python debug_with_inspector.py --check
      - run: python debug_with_inspector.py --test standard --method tools/list
```

## 📚 Additional Resources

- [MCP Inspector GitHub](https://github.com/modelcontextprotocol/inspector)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [OuiComply Documentation](./README.md)
- [API Documentation](./API_DOCUMENTATION.md)

## 🤝 Contributing

To improve debugging tools:

1. Fork the repository
2. Create a feature branch
3. Add new debugging features
4. Test with multiple server types
5. Submit a pull request

## 📄 License

This debugging guide is part of the OuiComply project and is licensed under the Apache License 2.0.
