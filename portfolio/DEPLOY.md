# 🚀 Deployment Guide — ApexStock Enterprise Portfolio

This portfolio website is **Render Deploy Ready** out of the box. You can deploy it in under **2 minutes** using any of the options below.

---

## 🌟 Option 1: Deploy to Render as a Static Site (Recommended — 100% Free)

Render's Static Site hosting gives you an instant global CDN, automatic SSL certificates, and zero server spin-down or cold starts.

### Steps:
1. Push your repository to **GitHub** or **GitLab**.
2. Sign in to your [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** $\rightarrow$ **Static Site**.
4. Connect your repository.
5. In the configuration page, specify:
   - **Name:** `apexstock-portfolio` *(or your preferred name)*
   - **Root Directory:** `portfolio` *(if your repo contains the root mini-pro folder)* or leave blank if deploying just this folder.
   - **Build Command:** *(leave empty)*
   - **Publish Directory:** `.` *(current directory)*
6. Click **Create Static Site**.
7. Your portfolio will be live at `https://apexstock-portfolio.onrender.com` in approximately 30 seconds!

---

## ⚡ Option 2: Deploy to Render using Blueprints (`render.yaml`)

The repository includes a pre-configured `render.yaml` blueprint.

### Steps:
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** $\rightarrow$ **Blueprint**.
3. Select your repository.
4. Render will detect `render.yaml` and configure both the Static Site and Node Web Service options automatically.
5. Click **Apply**.

---

## 💻 Option 3: Deploy to Render as a Node.js Web Service

If you prefer running a dedicated Express web server with health monitoring:

### Steps:
1. Click **New +** $\rightarrow$ **Web Service**.
2. Connect your repo and set:
   - **Root Directory:** `portfolio`
   - **Environment:** `Node`
   - **Build Command:** `npm install`
   - **Start Command:** `npm start`
   - **Health Check Path:** `/healthz`
3. Click **Create Web Service**.

---

## 🐍 Option 4: Local Development & Testing

You can run the portfolio locally on your machine with either Node.js or Python:

### With Node.js:
```bash
cd portfolio
npm install
npm start
# Open http://localhost:3000
```

### With Python:
```bash
cd portfolio
python server.py
# Open http://localhost:3000
```

---

## 🌐 Other Free Static Hosting Providers

This project is pure standards-compliant HTML5/CSS3/Vanilla JS and can also be hosted on:
- **Vercel:** Drag and drop the `portfolio` folder onto Vercel dashboard.
- **Netlify:** Drag and drop the `portfolio` folder into Netlify Drop.
- **GitHub Pages:** Go to Repo Settings $\rightarrow$ Pages $\rightarrow$ Set branch and directory.
