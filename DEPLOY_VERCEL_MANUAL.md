# Manual Vercel Deployment Guide

This guide provides step-by-step instructions for manually deploying the OuiComply MCP Server to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Node.js**: Install Node.js to use Vercel CLI (optional but recommended)

## Step 1: Install Vercel CLI

### Option A: Using npm (Recommended)
```bash
npm install -g vercel
```

### Option B: Using yarn
```bash
yarn global add vercel
```

### Option C: Using pnpm
```bash
pnpm add -g vercel
```

## Step 2: Prepare Your Repository

Ensure your repository contains these files:
- `vercel.json` - Vercel configuration
- `api/mcp.py` - Main MCP server API route
- `api/health.py` - Health check endpoint
- `requirements.txt` - Python dependencies
- `src/` directory with your tools

## Step 3: Deploy to Vercel

### Method 1: Using Vercel CLI

1. **Login to Vercel**:
   ```bash
   vercel login
   ```

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Follow the prompts**:
   - Set up and deploy? `Y`
   - Which scope? Choose your account
   - Link to existing project? `N` (for first deployment)
   - What's your project's name? `ouicomply-mcp` (or your preferred name)
   - In which directory is your code located? `./` (current directory)

### Method 2: Using Vercel Dashboard

1. **Go to Vercel Dashboard**:
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Import Project**:
   - Click "New Project"
   - Import your GitHub repository

3. **Configure Project**:
   - Framework Preset: `Other`
   - Root Directory: `./` (or leave empty)
   - Build Command: Leave empty
   - Output Directory: Leave empty

4. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete

## Step 4: Set Environment Variables

1. **Go to Project Settings**:
   - In your Vercel dashboard, select your project
   - Go to "Settings" → "Environment Variables"

2. **Add Required Variables**:
   ```
   MISTRAL_API_KEY=your_mistral_api_key_here
   LECHAT_API_KEY=your_lechat_api_key_here (optional)
   LOG_LEVEL=INFO
   ```

3. **Redeploy**:
   - After adding environment variables, redeploy your project
   - Go to "Deployments" tab
   - Click "Redeploy" on the latest deployment

## Step 5: Test Your Deployment

1. **Get Your Deployment URL**:
   - After deployment, you'll get a URL like `https://your-app.vercel.app`

2. **Test Health Check**:
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

## Step 6: Configure Le Chat

1. **Get Your MCP Server URL**:
   ```
   https://your-app.vercel.app/mcp
   ```

2. **Add to Le Chat**:
   - Open Le Chat settings
   - Add MCP server with your URL
   - Test the connection

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version is compatible (3.8+)

2. **Import Errors**:
   - Verify that `src/` directory is included in deployment
   - Check that all imports are correct

3. **Environment Variables**:
   - Ensure all required variables are set
   - Redeploy after adding new variables

4. **Timeout Issues**:
   - Vercel has a 10-second timeout for serverless functions
   - Optimize long-running operations

### Debugging

1. **Check Vercel Logs**:
   - Go to your project dashboard
   - Click on "Functions" tab
   - View logs for debugging

2. **Test Locally**:
   ```bash
   vercel dev
   ```
   - This runs your functions locally
   - Helps debug issues before deployment

3. **Health Check**:
   - Always test `/health` endpoint first
   - This verifies basic connectivity

## Success!

Once deployed, your MCP server will be available at:
- **MCP Endpoint**: `https://your-app.vercel.app/mcp`
- **Health Check**: `https://your-app.vercel.app/health`

You can now integrate this with Le Chat or any other MCP-compatible client!

## Next Steps

1. **Monitor Usage**: Check Vercel analytics for function invocations
2. **Set Up Monitoring**: Add logging and monitoring as needed
3. **Scale**: Vercel automatically scales based on usage
4. **Update**: Push changes to GitHub to automatically redeploy

## Support

If you encounter issues:
1. Check the Vercel documentation
2. Review the logs in your Vercel dashboard
3. Test locally with `vercel dev`
4. Verify all environment variables are set correctly
