# OuiComply MCP Server with ngrok Web Exposure

This guide explains how to expose the OuiComply MCP Server to the web using ngrok for testing and ALPIC integration.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **ngrok** installed and configured
3. **Virtual environment** activated (recommended)

### Installation

1. **Install ngrok** (if not already installed):
   ```bash
   # Download from https://ngrok.com/download
   # Or use package manager:
   # Windows: choco install ngrok
   # macOS: brew install ngrok
   # Linux: snap install ngrok
   ```

2. **Set up ngrok authentication** (optional but recommended):
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

#### Option 1: Python Script (Recommended)
```bash
python run_ngrok_mcp.py
```

#### Option 2: Windows Batch Script
```bash
start_ngrok_mcp.bat
```

#### Option 3: PowerShell Script
```powershell
.\start_ngrok_mcp.ps1
```

## 🔧 Configuration

### Environment Variables

You can configure the server using environment variables:

```bash
# Set port (default: 8000)
export PORT=8000

# Set Mistral API key
export MISTRAL_API_KEY=your_api_key_here

# Set server name
export SERVER_NAME="OuiComply MCP Server"
```

### ngrok Configuration

Create a `ngrok.yml` file in your home directory for advanced configuration:

```yaml
version: "2"
authtoken: YOUR_AUTHTOKEN
tunnels:
  mcp-server:
    proto: http
    addr: 8000
    subdomain: ouicomply-mcp  # Optional: custom subdomain
    region: us  # Optional: region selection
```

## 🧪 Testing

### Automated Testing

Run the comprehensive test suite:

```bash
python test_ngrok_mcp.py https://your-ngrok-url.ngrok.io
```

### Manual Testing

1. **Health Check**:
   ```bash
   curl https://your-ngrok-url.ngrok.io/health
   ```

2. **Server Info**:
   ```bash
   curl https://your-ngrok-url.ngrok.io/info
   ```

3. **MCP Initialize**:
   ```bash
   curl -X POST https://your-ngrok-url.ngrok.io/mcp \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "initialize",
       "params": {
         "protocolVersion": "2024-11-05",
         "capabilities": {},
         "clientInfo": {
           "name": "test-client",
           "version": "1.0.0"
         }
       }
     }'
   ```

4. **List Tools**:
   ```bash
   curl -X POST https://your-ngrok-url.ngrok.io/mcp \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 2,
       "method": "tools/list",
       "params": {}
     }'
   ```

## 🔗 Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check (same as `/health`) |
| `/health` | GET | Server health status |
| `/info` | GET | Server information and capabilities |
| `/mcp` | GET/POST | MCP protocol endpoint |
| `/mcp/` | GET/POST | MCP protocol endpoint (with trailing slash) |
| `/ssc` | GET/POST | SSC compatible endpoint (LeChat) |
| `/ssc/` | GET/POST | SSC compatible endpoint (with trailing slash) |

## 🤖 ALPIC Integration

### For ALPIC Configuration

Use the ngrok URL in your ALPIC configuration:

```json
{
  "mcp_servers": {
    "ouicomply": {
      "url": "https://your-ngrok-url.ngrok.io/mcp",
      "name": "OuiComply MCP Server",
      "description": "AI-assisted legal compliance checker"
    }
  }
}
```

### For LeChat Integration

Use the SSC endpoint for LeChat compatibility:

```json
{
  "mcp_servers": {
    "ouicomply": {
      "url": "https://your-ngrok-url.ngrok.io/ssc",
      "name": "OuiComply MCP Server (SSC)",
      "description": "AI-assisted legal compliance checker - LeChat compatible"
    }
  }
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **ngrok not found**:
   - Ensure ngrok is installed and in your PATH
   - Try running `ngrok version` to verify installation

2. **Port already in use**:
   - Change the port using `export PORT=8001`
   - Or kill the process using the port

3. **ngrok tunnel fails**:
   - Check your internet connection
   - Verify ngrok authentication token
   - Try restarting ngrok

4. **MCP server errors**:
   - Check Python dependencies: `pip install -r requirements.txt`
   - Verify Mistral API key is set
   - Check server logs for detailed error messages

### Debug Mode

Run with debug logging:

```bash
export LOG_LEVEL=DEBUG
python run_ngrok_mcp.py
```

### ngrok Web Interface

Access the ngrok web interface at `http://localhost:4040` to:
- View tunnel status
- Monitor requests
- Debug connection issues

## 📊 Monitoring

### Health Monitoring

The server provides several monitoring endpoints:

- **Health Check**: `/health` - Basic server status
- **Info Endpoint**: `/info` - Detailed server information
- **ngrok Interface**: `http://localhost:4040` - Tunnel monitoring

### Logs

Server logs include:
- Request/response details
- Error messages
- Performance metrics
- ngrok tunnel status

## 🔒 Security Considerations

### Current Security

- **No Authentication**: Server is open for all requests
- **Public Access**: ngrok tunnel is publicly accessible
- **HTTPS**: ngrok provides HTTPS by default

### Production Recommendations

For production use, consider:

1. **Authentication**: Implement API key or OAuth authentication
2. **Rate Limiting**: Add request rate limiting
3. **IP Whitelisting**: Restrict access to known IPs
4. **Custom Domain**: Use ngrok custom domain with SSL
5. **Monitoring**: Implement comprehensive monitoring and alerting

## 🚀 Advanced Usage

### Custom ngrok Configuration

Create a custom ngrok configuration:

```yaml
version: "2"
authtoken: YOUR_AUTHTOKEN
tunnels:
  mcp-server:
    proto: http
    addr: 8000
    subdomain: ouicomply-mcp
    region: us
    inspect: false
    bind_tls: true
    host_header: rewrite
```

### Multiple Tunnels

Run multiple MCP servers:

```yaml
version: "2"
tunnels:
  mcp-server-1:
    proto: http
    addr: 8000
    subdomain: ouicomply-mcp-1
  mcp-server-2:
    proto: http
    addr: 8001
    subdomain: ouicomply-mcp-2
```

### Load Balancing

Use ngrok's load balancing features for high availability:

```yaml
version: "2"
tunnels:
  mcp-server:
    proto: http
    addr: 8000
    subdomain: ouicomply-mcp
    host_header: rewrite
    # Add multiple upstream servers
```

## 📝 Examples

### Complete Test Workflow

```bash
# 1. Start the server
python run_ngrok_mcp.py

# 2. In another terminal, test the server
python test_ngrok_mcp.py https://abc123.ngrok.io

# 3. Test specific endpoints
curl https://abc123.ngrok.io/health
curl https://abc123.ngrok.io/info
```

### Integration with ALPIC

```python
# Example ALPIC integration
import requests

mcp_url = "https://your-ngrok-url.ngrok.io/mcp"

# Initialize MCP connection
init_payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "ALPIC",
            "version": "1.0.0"
        }
    }
}

response = requests.post(mcp_url, json=init_payload)
print(response.json())
```

## 🎯 Next Steps

1. **Test the server** using the provided test suite
2. **Integrate with ALPIC** using the ngrok URL
3. **Monitor performance** using the health endpoints
4. **Scale as needed** using ngrok's advanced features

## 📞 Support

For issues or questions:

1. Check the troubleshooting section above
2. Review server logs for error details
3. Test with the provided test suite
4. Check ngrok documentation for tunnel issues

---

**Happy testing! 🚀**
