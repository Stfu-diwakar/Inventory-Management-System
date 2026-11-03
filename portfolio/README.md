# 📦 ApexStock Enterprise — Portfolio Website

> **Academic Portfolio & Project Showcase Website**  
> **Institution:** University Institute of Computing &bull; Chandigarh University &bull; MCA (Artificial Intelligence & Machine Learning)  
> **Author:** Diwakar Jha (25MCI10342)  
> **Project:** Enterprise Inventory Management System (Oracle SQL 23ai + Streamlit)  

---

## 🌟 Overview

This folder contains a modern, responsive single-page portfolio website designed to showcase and explain the **ApexStock Enterprise Inventory Management System**.

It serves as both an interactive project presentation for faculty examiners during viva defense and a deployable portfolio site ready for cloud hosting on **Render.com**.

### ✨ Highlights
- **Interactive Oracle SQL Workbench Simulator:** Run curated viva SQL demonstrations (Joins, Window functions, Aggregations, Subqueries, MERGE upsert, and Data Dictionary checks) with simulated Oracle execution timings and CBO Cost Explain Plans.
- **Interactive Relational Schema (ERD) Explorer:** Visual schema cards for all 10 tables with primary/foreign keys, check constraints, normalization details, and 1-click DDL syntax viewing.
- **3-Tier Enterprise Architecture Deep Dive:** Presentation layer, Python-Oracle DAL, and Oracle 23ai engine breakdowns with ACID transaction diagrams.
- **Application UI Tour:** Interactive walkthrough of all 9 Streamlit application views with mockup previews and feature checklists.
- **Viva Defense Guide:** 5-step structured viva demonstration sequence and top examiner questions & answers on 3NF, MVCC, triggers, and parameterized queries.
- **Render Deploy Ready:** Includes `render.yaml`, `package.json`, `server.js` (Express), `server.py` (Python fallback), and `Procfile`.

---

## 📁 Directory Structure

```
portfolio/
│
├── index.html            # Main semantic HTML5 single-page application
├── css/
│   └── style.css         # Dark enterprise corporate design system (CSS3 variables, responsive)
├── js/
│   └── main.js           # Interactive SQL simulator, ERD modals, UI tabs, and animations
├── assets/
│   └── cu.png            # Chandigarh University crest / logo
│
├── render.yaml           # Render.com Blueprint configuration (Static Site & Web Service)
├── package.json          # Node.js Express server dependencies & scripts
├── server.js             # Production Node.js Express server with Gzip & healthchecks
├── server.py             # Zero-dependency Python HTTP server fallback
├── Procfile              # PaaS process file (web: node server.js)
├── DEPLOY.md             # Detailed 2-minute deployment guide for Render, Vercel, Netlify
└── README.md             # This documentation file
```

---

## 🚀 Quick Launch (Local Testing)

### Option A: Using Node.js
```bash
cd portfolio
npm install
npm start
```
Visit 👉 `http://localhost:3000`

### Option B: Using Python
```bash
cd portfolio
python server.py
```
Visit 👉 `http://localhost:3000`

---

## ☁️ Deploy to Render.com

See [`DEPLOY.md`](DEPLOY.md) for complete instructions. Render can deploy this site either as a **Static Site** (100% free, instant global CDN) or as a **Node Web Service**.
