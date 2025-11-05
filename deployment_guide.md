# Deployment Guide

This guide will help you deploy the Google Forms Generator application to the public internet.

## Prerequisites

1. **Python 3.7+** installed
2. **Google Cloud Project** with APIs enabled:
   - Google Forms API
   - Google Drive API
   - Google Docs API (optional, for Docs link feature)
3. **OAuth 2.0 Credentials** downloaded as `credentials.json`
4. **Google Gemini API Key** (for AI features)

## Quick Start (Local Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_api_key_here"
export SECRET_KEY="your_secret_key_here"

# Run the application
python app.py
```

## Deployment Options

### Option 1: Deploy with Gunicorn (Recommended for VPS/Cloud)

1. **Install Gunicorn:**
   ```bash
   pip install gunicorn
   ```

2. **Set environment variables:**
   ```bash
   export GEMINI_API_KEY="your_api_key"
   export SECRET_KEY="your_secret_key"
   export FLASK_ENV="production"
   export DEBUG="False"
   ```

3. **Run with Gunicorn:**
   ```bash
   gunicorn --config gunicorn_config.py app:app
   ```

4. **Or use systemd service** (create `/etc/systemd/system/google-form-generator.service`):
   ```ini
   [Unit]
   Description=Google Form Generator
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/GoogleFormGenerate
   Environment="PATH=/path/to/venv/bin"
   Environment="GEMINI_API_KEY=your_key"
   Environment="SECRET_KEY=your_secret_key"
   ExecStart=/path/to/venv/bin/gunicorn --config gunicorn_config.py app:app

   [Install]
   WantedBy=multi-user.target
   ```

### Option 2: Deploy with Docker

1. **Build the Docker image:**
   ```bash
   docker build -t google-form-generator .
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Or run directly:**
   ```bash
   docker run -d \
     -p 5000:5000 \
     -e GEMINI_API_KEY="your_key" \
     -e SECRET_KEY="your_secret_key" \
     -v $(pwd)/credentials.json:/app/credentials.json:ro \
     -v $(pwd)/token.pickle:/app/token.pickle \
     google-form-generator
   ```

### Option 3: Deploy to Cloud Platforms

#### Heroku

1. **Install Heroku CLI**
2. **Create `Procfile`:**
   ```
   web: gunicorn --config gunicorn_config.py app:app
   ```
3. **Set environment variables:**
   ```bash
   heroku config:set GEMINI_API_KEY=your_key
   heroku config:set SECRET_KEY=your_secret_key
   ```
4. **Deploy:**
   ```bash
   git push heroku main
   ```

#### Railway

1. **Connect your GitHub repository**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically**

#### Render

1. **Create new Web Service**
2. **Set build command:** `pip install -r requirements.txt`
3. **Set start command:** `gunicorn --config gunicorn_config.py app:app`
4. **Set environment variables**

#### Google Cloud Run

1. **Build and push container:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/google-form-generator
   ```
2. **Deploy:**
   ```bash
   gcloud run deploy google-form-generator \
     --image gcr.io/PROJECT_ID/google-form-generator \
     --platform managed \
     --set-env-vars GEMINI_API_KEY=your_key,SECRET_KEY=your_secret_key
   ```

## Security Checklist

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `GEMINI_API_KEY` as environment variable (never commit to git)
- [ ] Set `DEBUG=False` in production
- [ ] Use HTTPS (configure reverse proxy like Nginx)
- [ ] Set up proper CORS if needed
- [ ] Configure firewall rules
- [ ] Set up rate limiting (optional but recommended)
- [ ] Regular security updates
- [ ] Backup `credentials.json` and `token.pickle` securely

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `SECRET_KEY` | Flask secret key | Yes | Auto-generated |
| `FLASK_ENV` | Environment (development/production) | No | development |
| `DEBUG` | Enable debug mode | No | False |
| `HOST` | Host to bind | No | 0.0.0.0 |
| `PORT` | Port to bind | No | 5000 |
| `LOG_LEVEL` | Logging level | No | info |

## Reverse Proxy Setup (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## SSL/TLS Setup

Use Let's Encrypt for free SSL certificates:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring

- Set up application monitoring (e.g., Sentry, LogRocket)
- Monitor server resources (CPU, memory, disk)
- Set up uptime monitoring
- Configure log aggregation

## Backup

Important files to backup:
- `credentials.json` - OAuth credentials
- `token.pickle` - User authentication tokens
- Database files (if any)
- Configuration files

## Troubleshooting

1. **Check logs:**
   ```bash
   # Gunicorn logs
   tail -f /var/log/gunicorn/error.log
   
   # Docker logs
   docker logs google-form-generator
   ```

2. **Verify environment variables:**
   ```bash
   env | grep GEMINI
   env | grep SECRET
   ```

3. **Test API endpoint:**
   ```bash
   curl http://localhost:5000/api/health
   ```

## Support

For issues or questions, check the main README.md file.

