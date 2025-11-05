# 🚀 Deploy to Render.com - Step by Step (5 Minutes)

## Prerequisites
- GitHub account
- Your code pushed to GitHub

## Step 1: Push Code to GitHub

```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

## Step 2: Deploy on Render

1. **Go to:** https://render.com
2. **Sign up** with GitHub (free)
3. **Click:** "New +" → "Web Service"
4. **Connect** your GitHub repository
5. **Configure:**
   - **Name:** `google-form-generator` (or any name)
   - **Region:** Choose closest to you
   - **Branch:** `main` (or `master`)
   - **Root Directory:** (leave empty)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --config gunicorn_config.py app:app`

6. **Add Environment Variables:**
   - Click "Add Environment Variable"
   - Add these one by one:
     ```
     GEMINI_API_KEY = AIzaSyCzlgkxBgZ2gbF-WxHwE-v9Emw1JeHEYaY
     SECRET_KEY = (generate with command below)
     FLASK_ENV = production
     DEBUG = False
     PORT = 5000
     ```

7. **Generate Secret Key:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copy the output and use it as `SECRET_KEY`

8. **Click:** "Create Web Service"

## Step 3: Upload Credentials

After deployment starts, you need to upload `credentials.json`:

1. Go to your service dashboard
2. Click "Shell" tab (or use SSH)
3. Upload `credentials.json`:
   ```bash
   # In Render Shell
   cat > credentials.json << 'EOF'
   [paste your credentials.json content here]
   EOF
   ```

4. Or use Render's file system if available

## Step 4: Test

1. Wait for deployment to complete (~2-3 minutes)
2. Visit your app URL: `https://your-app-name.onrender.com`
3. First request may take 30 seconds (cold start)
4. Test the form creation!

## Troubleshooting

### App sleeps after 15 minutes
- **Normal behavior** on free tier
- First request after sleep takes ~30 seconds
- Consider Railway or Fly.io for always-on

### Credentials not found
- Make sure `credentials.json` is in the root directory
- Check Render Shell to verify file exists

### Build fails
- Check build logs in Render dashboard
- Make sure `requirements.txt` includes all dependencies
- Verify Python version compatibility

## That's It! 🎉

Your app is now live at: `https://your-app-name.onrender.com`

**Cost:** FREE (with 15min sleep after inactivity)

