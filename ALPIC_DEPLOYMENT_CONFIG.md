# Alpic Deployment Configuration Guide

## 🚀 **Deployment Settings for Alpic Interface**

Based on your working Flask MCP server, here are the exact settings to populate in the Alpic deployment interface:

### **1. Runtime Configuration**
- **Runtime**: `Python 3.12` ✅ (Updated from 3.11)
- **Entrypoint**: `mcp_server_flask.py` ✅
- **Port**: `8000` ✅

### **2. Environment Variables**
Copy these exact key-value pairs into the Environment Variables section:

| Key | Value | Secret |
|-----|-------|--------|
| `MISTRAL_KEY` | `Gr9ZoQBFhi3tk85GChM6NjfcfOgg0XPW` | ✅ Yes |
| `LECHAT_API_URL` | `https://api.lechat.ai` | ❌ No |
| `LECHAT_API_KEY` | `your_lechat_api_key_here` | ✅ Yes |
| `MCP_SERVER_NAME` | `ouicomply-mcp` | ❌ No |
| `MCP_SERVER_VERSION` | `1.0.0` | ❌ No |
| `MCP_SERVER_PORT` | `8000` | ❌ No |
| `LOG_LEVEL` | `INFO` | ❌ No |
| `FLASK_ENV` | `production` | ❌ No |
| `PYTHONPATH` | `/app` | ❌ No |

### **3. Build Settings**
- **Install Command**: `pip install -r requirements_mcp.txt` ✅
- **Start Command**: `python mcp_server_flask.py` ✅

### **4. Key Features Ready**
- ✅ **MCP Protocol** - Full compliance with Le Chat requirements
- ✅ **Server-Sent Events** - Real-time communication via `/mcp/sse`
- ✅ **Tool Calling** - 3 tools: analyze_document, update_memory, get_compliance_status
- ✅ **Resource Management** - Compliance frameworks and team memory
- ✅ **Health Monitoring** - `/health` endpoint for status checks
- ✅ **CORS Support** - Web integration ready

### **5. Endpoints Available**
- `GET /health` - Health check
- `POST /mcp` - MCP protocol endpoint
- `GET /mcp/sse` - Server-Sent Events
- `GET /lechat/integration` - Le Chat integration info
- `GET /` - Root endpoint with capabilities

### **6. Dependencies Included**
All required packages are in `requirements_mcp.txt`:
- Flask 3.1.2+ (web framework)
- Flask-CORS 6.0.1+ (CORS support)
- Mistral AI 1.9.10+ (AI services)
- Pydantic 2.10.3+ (data validation)
- Requests 2.32.3+ (HTTP client)

### **7. Testing Status**
- ✅ **Local Testing**: All endpoints working on port 8006
- ✅ **MCP Protocol**: Initialize, tools/list, tools/call all functional
- ✅ **SSE Streaming**: Real-time events working
- ✅ **Health Checks**: Status monitoring operational
- ✅ **CORS**: Cross-origin requests enabled

### **8. Deployment Checklist**
- [ ] Set `MISTRAL_KEY` as secret environment variable
- [ ] Update `LECHAT_API_KEY` with actual Le Chat API key
- [ ] Verify Python 3.12 runtime selection
- [ ] Confirm `mcp_server_flask.py` as entrypoint
- [ ] Set port to 8000
- [ ] Enable install command: `pip install -r requirements_mcp.txt`
- [ ] Enable start command: `python mcp_server_flask.py`

### **9. Post-Deployment Testing**
After deployment, test these URLs:
- `https://your-app.alpic.com/health` - Should return server status
- `https://your-app.alpic.com/mcp` - MCP protocol endpoint
- `https://your-app.alpic.com/lechat/integration` - Integration info

### **10. Le Chat Integration**
Once deployed, add this URL to Le Chat:
```
https://your-app.alpic.com/mcp
```

The server will automatically provide:
- Tool discovery and calling
- Resource management
- Real-time updates via SSE
- Compliance analysis capabilities

---

## 🎯 **Ready to Deploy!**

Your Flask MCP server is fully tested and ready for Alpic deployment. All configuration files are updated and the server has been verified to work correctly with Le Chat's MCP protocol requirements.
