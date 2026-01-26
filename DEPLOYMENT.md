# Railway Deployment Configuration
# This Flask app is not compatible with Netlify (static hosting only)

## ⚠️ IMPORTANT: This is a Flask Web Application

**Netlify is designed for static sites only** and cannot host Flask applications. 

### Recommended Hosting Platforms:

#### 1. **Render** (Easiest - Free Tier Available)
- Upload `render.yaml` (already created in repo)
- Connect your GitHub repository
- Automatic deployments on push
- **Free tier includes**: 750 hours/month

#### 2. **Railway** (Developer-Friendly)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### 3. **Heroku** (Classic Choice)
```bash
# Install Heroku CLI, then:
heroku login
heroku create rla-cosmetics
git push heroku main
```

#### 4. **PythonAnywhere** (Python-Specific)
- Upload code via Git or web interface
- Configure WSGI file
- Free tier: 1 web app

### Environment Variables Required:
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///instance/cosmetics.db
```

### Build/Start Commands:
- **Build**: `pip install -r requirements.txt`
- **Start**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 'app:create_app()'`

### Files Created for Deployment:
- `render.yaml` - Render configuration
- `Procfile` - Heroku/Railway configuration
- `requirements.txt` - Python dependencies (already exists)
- `gunicorn_config.py` - Gunicorn configuration (already exists)

---

## Why Netlify Doesn't Work:

1. **Flask needs a persistent server** - Netlify only serves static files
2. **No Python runtime** - Netlify Functions have limited Python support
3. **Database requires file system** - Netlify's file system is read-only during runtime

If you want to use Netlify, you would need to:
- Build a separate frontend (React/Vue) → Host on Netlify
- Host Flask backend separately → Connect via API
- This would require significant restructuring
