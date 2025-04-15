# Domain Deployment Guide for License Plate Detection API

## Prerequisites

- Domain name (e.g., api.yourdomain.com)
- VPS/Cloud Server (Recommended: Ubuntu 20.04+)
- SSL Certificate
- Nginx
- Supervisor
- Python 3.8+

## 1. Server Setup

### 1.1 Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Install Required Packages

```bash
sudo apt install -y python3-pip python3-venv nginx supervisor
```

### 1.3 Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv /opt/license-plate-app/venv
source /opt/license-plate-app/venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## 2. Nginx Configuration

### 2.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/license-plate-detection
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2.2 Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/license-plate-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 3. SSL Setup (Let's Encrypt)

### 3.1 Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 3.2 Obtain SSL Certificate

```bash
sudo certbot --nginx -d api.yourdomain.com
```

## 4. Supervisor Configuration

### 4.1 Create Supervisor Config

```bash
sudo nano /etc/supervisor/conf.d/license-plate-app.conf
```

Add this configuration:

```ini
[program:license-plate-app]
command=/opt/license-plate-app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/opt/license-plate-app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/license-plate-app.err.log
stdout_logfile=/var/log/license-plate-app.out.log
```

### 4.2 Start Supervisor

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start license-plate-app
```

## 5. Firewall Configuration

```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

## 6. Testing the API

### 6.1 Check API Status

```bash
curl https://api.yourdomain.com/
```

### 6.2 Test Detection Endpoint

```bash
curl -X POST "https://api.yourdomain.com/api/v1/detect" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "image=@test_image.jpg"
```

## 7. Monitoring and Maintenance

### 7.1 Check Logs

```bash
# Application logs
sudo tail -f /var/log/license-plate-app.err.log
sudo tail -f /var/log/license-plate-app.out.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 7.2 Restart Services

```bash
# Restart API
sudo supervisorctl restart license-plate-app

# Restart Nginx
sudo systemctl restart nginx
```

## 8. Security Considerations

1. **Rate Limiting**
   - Implement rate limiting in Nginx
   - Add authentication middleware

2. **Backup**
   - Regular backups of:
     - Application code
     - Model files
     - Database (if any)

3. **Monitoring**
   - Set up monitoring for:
     - Server resources
     - API uptime
     - Error rates

## 9. Troubleshooting

### 9.1 Common Issues

1. **API Not Responding**

```bash
# Check supervisor status
sudo supervisorctl status

# Check logs
sudo tail -f /var/log/license-plate-app.err.log
```

2. **Nginx Issues**

```bash
# Check Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

3. **SSL Issues**

```bash
# Check SSL certificate
sudo certbot certificates

# Renew SSL certificate
sudo certbot renew
```

## 10. Example Client Code

### Python

```python
import requests

API_URL = "https://api.yourdomain.com/api/v1"

def detect_plate(image_path):
    with open(image_path, "rb") as f:
        files = {"image": f}
        response = requests.post(f"{API_URL}/detect", files=files)
    return response.json()

def process_image(car_image_path, custom_text=None):
    with open(car_image_path, "rb") as f:
        files = {"car_image": f}
        data = {"custom_text": custom_text} if custom_text else {}
        response = requests.post(f"{API_URL}/process", files=files, data=data)
    return response.content
```

### JavaScript

```javascript
async function detectPlate(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await fetch('https://api.yourdomain.com/api/v1/detect', {
        method: 'POST',
        body: formData
    });
    return await response.json();
}

async function processImage(carImageFile, customText) {
    const formData = new FormData();
    formData.append('car_image', carImageFile);
    if (customText) {
        formData.append('custom_text', customText);
    }

    const response = await fetch('https://api.yourdomain.com/api/v1/process', {
        method: 'POST',
        body: formData
    });
    return await response.blob();
}
```

## 11. Performance Optimization

1. **Caching**
   - Implement Redis caching for frequent requests
   - Cache model results

2. **Load Balancing**
   - Set up multiple API instances
   - Use Nginx as load balancer

3. **CDN**
   - Use CDN for static assets
   - Cache processed images

## 12. Backup and Recovery

### 12.1 Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/backup/license-plate-app"
DATE=$(date +%Y%m%d)

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup application code
cp -r /opt/license-plate-app $BACKUP_DIR/$DATE/

# Backup configuration
cp /etc/nginx/sites-available/license-plate-app $BACKUP_DIR/$DATE/
cp /etc/supervisor/conf.d/license-plate-app.conf $BACKUP_DIR/$DATE/

# Compress backup
tar -czf $BACKUP_DIR/license-plate-app-$DATE.tar.gz $BACKUP_DIR/$DATE/

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -type f -mtime +7 -delete
```

### 12.2 Recovery Process

```bash
# Stop services
sudo supervisorctl stop license-plate-app
sudo systemctl stop nginx

# Restore from backup
tar -xzf backup-file.tar.gz -C /

# Restart services
sudo supervisorctl start license-plate-app
sudo systemctl start nginx
```
