# OuiComply Deployment Guide

This guide covers various deployment options for the OuiComply MCP Server.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Mistral API key
- Git

### Local Development Setup

1. **Clone and setup**
   ```bash
   git clone https://github.com/yourusername/ouicomply.git
   cd ouicomply
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the server**
   ```bash
   python -m src.mcp_server
   ```

## 🌐 Vercel Deployment

### Prerequisites
- Vercel account
- Vercel CLI installed (`npm i -g vercel`)

### Steps

1. **Initialize Vercel project**
   ```bash
   vercel init
   ```

2. **Create vercel.json**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "src/mcp_server.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "src/mcp_server.py"
       }
     ],
     "env": {
       "MISTRAL_KEY": "@mistral-key",
       "LECHAT_API_KEY": "@lechat-api-key",
       "GITHUB_TOKEN": "@github-token"
     }
   }
   ```

3. **Set environment variables in Vercel dashboard**
   - Go to your project settings
   - Add environment variables:
     - `MISTRAL_KEY`: Your Mistral API key
     - `LECHAT_API_KEY`: Your LeChat API key (optional)
     - `GITHUB_TOKEN`: Your GitHub token (optional)

4. **Deploy**
   ```bash
   vercel --prod
   ```

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 3000

# Run the application
CMD ["python", "-m", "src.mcp_server"]
```

### Build and Run

```bash
# Build image
docker build -t ouicomply-mcp .

# Run container
docker run -p 3000:3000 \
  -e MISTRAL_KEY=your_mistral_api_key \
  -e LECHAT_API_KEY=your_lechat_api_key \
  ouicomply-mcp

# Or with .env file
docker run -p 3000:3000 --env-file .env ouicomply-mcp
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ouicomply-mcp:
    build: .
    ports:
      - "3000:3000"
    environment:
      - MISTRAL_KEY=${MISTRAL_KEY}
      - LECHAT_API_KEY=${LECHAT_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    env_file:
      - .env
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## ☁️ AWS Deployment

### Using AWS Lambda

1. **Install AWS SAM CLI**
   ```bash
   pip install aws-sam-cli
   ```

2. **Create template.yaml**
   ```yaml
   AWSTemplateFormatVersion: '2010-09-09'
   Transform: AWS::Serverless-2016-10-31
   
   Resources:
     OuiComplyFunction:
       Type: AWS::Serverless::Function
       Properties:
         CodeUri: .
         Handler: src.mcp_server.main
         Runtime: python3.11
         Environment:
           Variables:
             MISTRAL_KEY: !Ref MistralApiKey
             LECHAT_API_KEY: !Ref LeChatApiKey
         Events:
           Api:
             Type: Api
             Properties:
               Path: /{proxy+}
               Method: ANY
   
   Parameters:
     MistralApiKey:
       Type: String
       NoEcho: true
     LeChatApiKey:
       Type: String
       NoEcho: true
   ```

3. **Deploy**
   ```bash
   sam build
   sam deploy --guided
   ```

### Using AWS ECS

1. **Create ECS task definition**
   ```json
   {
     "family": "ouicomply-mcp",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "ouicomply-mcp",
         "image": "your-account.dkr.ecr.region.amazonaws.com/ouicomply-mcp:latest",
         "portMappings": [
           {
             "containerPort": 3000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "MISTRAL_KEY",
             "value": "your-mistral-api-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/ouicomply-mcp",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

2. **Create ECS service and deploy**

## 🔧 Google Cloud Platform

### Using Cloud Run

1. **Create cloudbuild.yaml**
   ```yaml
   steps:
     - name: 'gcr.io/cloud-builders/docker'
       args: ['build', '-t', 'gcr.io/$PROJECT_ID/ouicomply-mcp', '.']
     - name: 'gcr.io/cloud-builders/docker'
       args: ['push', 'gcr.io/$PROJECT_ID/ouicomply-mcp']
     - name: 'gcr.io/cloud-builders/gcloud'
       args: [
         'run', 'deploy', 'ouicomply-mcp',
         '--image', 'gcr.io/$PROJECT_ID/ouicomply-mcp',
         '--platform', 'managed',
         '--region', 'us-central1',
         '--allow-unauthenticated',
         '--set-env-vars', 'MISTRAL_KEY=your-mistral-api-key'
       ]
   ```

2. **Deploy**
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

## 🔒 Security Considerations

### Environment Variables
- Never commit API keys to version control
- Use secure secret management services
- Rotate API keys regularly
- Use least-privilege access

### Network Security
- Use HTTPS in production
- Implement proper CORS policies
- Use VPCs and security groups
- Enable logging and monitoring

### API Security
- Implement rate limiting
- Use authentication tokens
- Validate all inputs
- Monitor for suspicious activity

## 📊 Monitoring and Logging

### Health Checks
Add health check endpoint:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
```

### Logging Configuration
```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### Metrics Collection
- Use Prometheus for metrics
- Implement custom metrics for compliance analysis
- Monitor API response times
- Track error rates

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration
   - Verify virtual environment activation

2. **API Connection Issues**
   - Verify API keys are correct
   - Check network connectivity
   - Review API rate limits

3. **Memory Issues**
   - Monitor memory usage
   - Implement document size limits
   - Use streaming for large documents

4. **Performance Issues**
   - Profile the application
   - Implement caching
   - Optimize database queries

### Debug Mode
Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python -m src.mcp_server
```

### Log Analysis
```bash
# View logs in real-time
tail -f /var/log/ouicomply-mcp.log

# Search for errors
grep "ERROR" /var/log/ouicomply-mcp.log

# Monitor performance
grep "performance" /var/log/ouicomply-mcp.log
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy OuiComply MCP

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancers
- Implement stateless design
- Use shared storage for state
- Monitor resource usage

### Vertical Scaling
- Increase CPU and memory
- Optimize database queries
- Implement caching strategies
- Use CDN for static content

### Database Scaling
- Use read replicas
- Implement connection pooling
- Consider NoSQL for large datasets
- Monitor query performance

---

For additional deployment options or support, please refer to the main documentation or create an issue in the repository.
