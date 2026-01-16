# ProjectFlow - Project Management SaaS

A powerful, Monday.com-inspired project management application built with Django.

## 🚀 Features

- **Dynamic Boards**: Create custom boards with flexible columns (Status, Date, Text, People, etc.)
- **Automation Engine**: Build "If This Then That" rules with visual builder
- **Team Collaboration**: Invite members, manage roles, and permissions
- **Real-time Notifications**: In-app alerts for team activities and automations
- **Beautiful UI**: Premium design with animations and responsive layout
- **Marketing Pages**: Dynamic pricing and features pages

## 🛠️ Tech Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (development) / PostgreSQL (production)
- **Task Queue**: Celery + Redis
- **Frontend**: TailwindCSS (CDN), Alpine.js (CDN)
- **Icons**: Heroicons

## 📦 Installation

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd New_project
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
# DATABASE_URL=postgresql://user:password@localhost/dbname

# Email (for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Collect Static Files (Production)
```bash
python manage.py collectstatic
```

### 8. Run Development Server
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

## 🔧 Running Celery (Background Tasks)

### Install Redis
- **Windows**: Download from https://github.com/microsoftarchive/redis/releases
- **Mac**: `brew install redis`
- **Linux**: `sudo apt-get install redis-server`

### Start Redis
```bash
redis-server
```

### Start Celery Worker
```bash
# Windows
celery -A config worker --loglevel=info --pool=solo

# Mac/Linux
celery -A config worker --loglevel=info
```

## 📂 Project Structure

```
New_project/
├── automation/          # Automation engine (triggers, actions, rules)
├── config/             # Django settings and configuration
├── core/               # User auth, notifications, billing
├── marketing/          # Landing pages, pricing, features
├── webapp/             # Main app (boards, items, columns)
├── templates/          # HTML templates
│   ├── automation/
│   ├── core/
│   ├── marketing/
│   └── webapp/
├── static/             # CSS, JavaScript, images
│   ├── css/
│   ├── js/
│   └── images/
├── manage.py
├── requirements.txt
└── README.md
```

## 🎨 Admin Panel

Access Django Admin at: `http://127.0.0.1:8000/admin/`

### Populate Dynamic Content

1. **Automation**:
   - Add `TriggerType` records (e.g., "Status Changed", "Item Created")
   - Add `ActionType` records (e.g., "Send Email", "Change Status")

2. **Features**:
   - Add `Feature` records for the Features page

3. **Pricing**:
   - Add `PricingPlan` records for the Pricing page

## 🚀 Production Deployment

### 1. Update Settings
In `config/settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

### 2. Use PostgreSQL
```bash
pip install psycopg2-binary
```

Update `DATABASES` in settings.py or use `DATABASE_URL` environment variable.

### 3. Configure Static Files
```python
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

Run:
```bash
python manage.py collectstatic
```

### 4. Use Gunicorn
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### 5. Setup Nginx (Reverse Proxy)
Example Nginx config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/New_project/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📝 License

Proprietary - All rights reserved

## 🤝 Support

For support, email: support@projectflow.com

---

**Built with ❤️ using Django**
