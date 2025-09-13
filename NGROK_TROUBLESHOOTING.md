# ngrok Troubleshooting Guide

## 🚨 Current Issue: TLS Certificate Verification Error

You're experiencing this error:
```
failed to send authentication request: tls: failed to verify certificate: x509: certificate signed by unknown authority
```

This is typically caused by:
1. Corporate firewall/proxy settings
2. Antivirus software interfering with TLS
3. Network security policies
4. Outdated ngrok version

## 🔧 Solutions

### Solution 1: Fix ngrok TLS Issues

#### Option A: Update ngrok and authenticate
```bash
# Download latest ngrok from https://ngrok.com/download
# Or update via package manager

# Add your auth token (get from https://dashboard.ngrok.com/get-started/your-authtoken)
ngrok config add-authtoken YOUR_AUTHTOKEN

# Try again
ngrok http 3000
```

#### Option B: Bypass TLS verification (NOT recommended for production)
```bash
# Set environment variable to skip TLS verification
$env:NGROK_SKIP_VERIFY="true"
ngrok http 3000
```

#### Option C: Use ngrok with custom configuration
Create `ngrok.yml` in your home directory:
```yaml
version: "2"
authtoken: YOUR_AUTHTOKEN
tunnels:
  mcp-server:
    proto: http
    addr: 3000
    inspect: false
    bind_tls: true
    host_header: rewrite
```

Then run:
```bash
ngrok start mcp-server
```

### Solution 2: Alternative Tunneling Methods

#### Option A: Use localtunnel (Node.js required)
```bash
# Install localtunnel
npm install -g localtunnel

# Start your MCP server
python run_ngrok_mcp.py

# In another terminal, create tunnel
lt --port 3000 --subdomain ouicomply-mcp
```

#### Option B: Use serveo (no installation required)
```bash
# Start your MCP server
python run_ngrok_mcp.py

# In another terminal, create tunnel
ssh -R 80:localhost:3000 serveo.net
```

#### Option C: Use cloudflared tunnel
```bash
# Download cloudflared from https://github.com/cloudflare/cloudflared/releases

# Start your MCP server
python run_ngrok_mcp.py

# Create tunnel
cloudflared tunnel --url http://localhost:3000
```

### Solution 3: Local Network Access

If you only need access from your local network:

```bash
# Start MCP server
python run_ngrok_mcp.py

# Find your local IP
ipconfig

# Access from other devices on same network
# http://YOUR_LOCAL_IP:3000/health
```

## 🧪 Testing Your Setup

### Test Local Server
```bash
# Test health endpoint
curl http://localhost:3000/health

# Test MCP endpoint
curl http://localhost:3000/mcp

# Test with POST request
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

### Test Tunnel (once working)
```bash
# Replace YOUR_TUNNEL_URL with actual tunnel URL
curl https://YOUR_TUNNEL_URL.ngrok.io/health
curl https://YOUR_TUNNEL_URL.ngrok.io/mcp
```

## 🔍 Debugging Steps

### 1. Check ngrok status
```bash
# Check if ngrok is running
Get-Process | Where-Object {$_.ProcessName -like "*ngrok*"}

# Check ngrok web interface
curl http://localhost:4040/api/tunnels
```

### 2. Check MCP server status
```bash
# Check if Python server is running
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# Test local endpoints
curl http://localhost:3000/health
```

### 3. Check network connectivity
```bash
# Test basic connectivity
ping google.com

# Test HTTPS connectivity
curl https://httpbin.org/get
```

## 🚀 Quick Fix for Current Issue

Since you're having TLS issues with ngrok, here's a quick workaround:

### Method 1: Use the simple test server
```bash
# Stop any running servers
taskkill /F /IM python3.12.exe
taskkill /F /IM ngrok.exe

# Start simple test server
python simple_ngrok_test.py
```

### Method 2: Use localtunnel (if you have Node.js)
```bash
# Install localtunnel
npm install -g localtunnel

# Start MCP server in one terminal
python run_ngrok_mcp.py

# In another terminal, create tunnel
lt --port 3000
```

### Method 3: Use serveo (no installation)
```bash
# Start MCP server in one terminal
python run_ngrok_mcp.py

# In another terminal, create tunnel
ssh -R 80:localhost:3000 serveo.net
```

## 📋 ALPIC Integration

Once you have a working tunnel URL, use it in your ALPIC configuration:

```json
{
  "mcp_servers": {
    "ouicomply": {
      "url": "https://YOUR_TUNNEL_URL/health",
      "name": "OuiComply MCP Server"
    }
  }
}
```

## 🆘 Still Having Issues?

1. **Check Windows Firewall**: Make sure port 3000 is allowed
2. **Check Antivirus**: Temporarily disable to test
3. **Try Different Port**: Use `$env:PORT="8080"` and update ngrok command
4. **Use HTTP instead of HTTPS**: Some corporate networks block HTTPS tunnels
5. **Contact IT**: If on corporate network, they may need to whitelist ngrok

## 📞 Support

If none of these solutions work:
1. Check the server logs for specific error messages
2. Try the alternative tunneling methods
3. Use local network access if possible
4. Consider using a different machine/network for testing

---

**The MCP server is working correctly on localhost:3000 - the issue is only with the ngrok tunnel creation.**
