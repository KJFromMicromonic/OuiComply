# Le Chat Integration - Tunneling Solutions

## 🚨 Current Status

The OuiComply MCP Server is running locally on `http://localhost:8000` but **ngrok is experiencing certificate verification issues** that prevent it from creating a public tunnel. This is a common issue with corporate networks or certain system configurations.

## 🛠️ Alternative Solutions for Le Chat Integration

### Option 1: Cloudflare Tunnel (Recommended)

Cloudflare Tunnel is a more reliable alternative to ngrok:

1. **Install Cloudflare Tunnel**:
   ```bash
   # Download from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   # Or use package manager
   ```

2. **Authenticate**:
   ```bash
   cloudflared tunnel login
   ```

3. **Create Tunnel**:
   ```bash
   cloudflared tunnel create ouicomply-mcp
   cloudflared tunnel route dns ouicomply-mcp ouicomply-mcp.yourdomain.com
   cloudflared tunnel run ouicomply-mcp --url http://localhost:8000
   ```

### Option 2: Deploy to Cloud Service

Deploy the MCP Server to a cloud service:

1. **Heroku**:
   ```bash
   # Create Procfile
   echo "web: python fastapi_simple.py" > Procfile
   
   # Deploy
   git init
   git add .
   git commit -m "Initial commit"
   heroku create ouicomply-mcp
   git push heroku main
   ```

2. **Railway**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Deploy
   railway login
   railway init
   railway up
   ```

3. **Render**:
   - Connect your GitHub repository
   - Set build command: `pip install -r requirements_fastapi.txt`
   - Set start command: `python fastapi_simple.py`

### Option 3: Use Different Tunneling Service

Try these alternatives:

1. **Serveo** (SSH-based):
   ```bash
   ssh -R 80:localhost:8000 serveo.net
   ```

2. **LocalTunnel** (if working):
   ```bash
   npx localtunnel --port 8000
   ```

3. **Bore** (Rust-based):
   ```bash
   # Install bore
   cargo install bore-cli
   
   # Create tunnel
   bore local 8000 --to bore.pub
   ```

### Option 4: Manual Port Forwarding

If you have access to your router:

1. **Enable Port Forwarding**:
   - Forward external port 8000 to internal port 8000
   - Note your public IP address

2. **Update Server Configuration**:
   ```python
   # In fastapi_simple.py, change:
   uvicorn.run(
       "fastapi_simple:app",
       host="0.0.0.0",  # Allow external connections
       port=8000,
       reload=False
   )
   ```

3. **Access via Public IP**:
   ```
   http://YOUR_PUBLIC_IP:8000
   ```

## 🧪 Testing Your Tunnel

Once you have a public URL, test it with:

```bash
# Test health endpoint
curl https://your-tunnel-url.com/health

# Test Le Chat integration
curl https://your-tunnel-url.com/lechat/integration

# Test document analysis
curl -X POST https://your-tunnel-url.com/lechat/test \
  -H "Content-Type: application/json" \
  -d '{
    "document_content": "Test document",
    "document_name": "test.txt",
    "team_context": "Legal Team"
  }'
```

## 🔧 Current Working Setup

### Local Testing
The MCP Server is currently running and can be tested locally:

- **URL**: `http://localhost:8000`
- **Health Check**: `http://localhost:8000/health`
- **Le Chat Integration**: `http://localhost:8000/lechat/integration`
- **Test Interface**: Open `mcp_server_test.html` in your browser

### Test the Local Server
```bash
# Run the test script
python test_lechat_integration.py

# Or open the HTML test interface
start mcp_server_test.html
```

## 📋 Le Chat Configuration

Once you have a public URL, configure Le Chat:

1. **Add MCP Server**:
   - URL: `https://your-tunnel-url.com`
   - Name: `OuiComply MCP Server`

2. **Test Integration**:
   - Use the `/lechat/test` endpoint
   - Send document analysis requests
   - Verify memory integration is working

## 🚀 Recommended Next Steps

1. **Try Cloudflare Tunnel** (most reliable)
2. **Deploy to a cloud service** (most permanent)
3. **Use the local test interface** for immediate testing
4. **Configure Le Chat** once you have a public URL

## 📞 Troubleshooting

### Common Issues

1. **Certificate Errors**: Use Cloudflare Tunnel or deploy to cloud
2. **Port Blocked**: Try different ports or use cloud deployment
3. **Network Restrictions**: Use VPN or cloud deployment
4. **Tunnel Unstable**: Use multiple tunnel services as backup

### Debug Commands

```bash
# Check if server is running
curl http://localhost:8000/health

# Check tunnel status
curl http://127.0.0.1:4040/api/tunnels  # For ngrok

# Test specific endpoint
curl -X POST http://localhost:8000/lechat/test \
  -H "Content-Type: application/json" \
  -d '{"document_content": "test", "document_name": "test.txt", "team_context": "Legal Team"}'
```

---

**Status**: ✅ MCP Server Ready, ⚠️ Tunnel Needed for Le Chat
**Local Testing**: ✅ Working
**Public Access**: ⚠️ Requires tunnel setup
**Le Chat Integration**: ⚠️ Waiting for public URL
