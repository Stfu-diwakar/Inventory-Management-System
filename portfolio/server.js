/**
 * ApexStock Enterprise Portfolio — Production Web Server
 * Render.com Deploy Ready (Node.js Express + Static Asset Pipeline)
 */

const http = require('http');
const path = require('path');
const fs = require('fs');

let express;
let compression;

try {
  express = require('express');
} catch (e) {
  // If express is not installed, fallback to native Node.js HTTP server
  express = null;
}

try {
  compression = require('compression');
} catch (e) {
  compression = null;
}

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.resolve(__dirname);

if (express) {
  const app = express();

  // 1. Enable GZIP compression if available
  if (compression) {
    app.use(compression());
  }

  // 2. Production Security Headers
  app.use((req, res, next) => {
    res.setHeader('X-Frame-Options', 'SAMEORIGIN');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    next();
  });

  // 3. Healthcheck Endpoint for Render Zero-Downtime Monitoring
  app.get('/healthz', (req, res) => {
    res.status(200).json({
      status: 'healthy',
      app: 'ApexStock Enterprise Portfolio',
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    });
  });

  // 4. Serve Static Files with Cache Headers
  app.use(express.static(PUBLIC_DIR, {
    maxAge: '1d',
    etag: true
  }));

  // 5. Fallback route for SPA navigation
  app.get('*', (req, res) => {
    res.sendFile(path.join(PUBLIC_DIR, 'index.html'));
  });

  const server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`====================================================`);
    console.log(`📦 ApexStock Portfolio Server is LIVE!`);
    console.log(`👉 Local:   http://localhost:${PORT}`);
    console.log(`👉 Health:  http://localhost:${PORT}/healthz`);
    console.log(`👉 Mode:    Express (Production Ready)`);
    console.log(`====================================================`);
  });

  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('SIGTERM signal received. Closing server gracefully...');
    server.close(() => {
      console.log('Server closed successfully.');
      process.exit(0);
    });
  });

} else {
  // Pure Native Node.js HTTP Server fallback (Zero-Dependency)
  const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
  };

  const server = http.createServer((req, res) => {
    if (req.url === '/healthz') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ status: 'healthy', mode: 'native-http' }));
    }

    let filePath = path.join(PUBLIC_DIR, req.url === '/' ? 'index.html' : req.url);
    const ext = path.extname(filePath).toLowerCase();

    fs.stat(filePath, (err, stats) => {
      if (err || !stats.isFile()) {
        filePath = path.join(PUBLIC_DIR, 'index.html');
      }

      fs.readFile(filePath, (readErr, content) => {
        if (readErr) {
          res.writeHead(500);
          return res.end('Internal Server Error');
        }
        const mime = MIME_TYPES[path.extname(filePath).toLowerCase()] || 'text/plain';
        res.writeHead(200, { 'Content-Type': mime });
        res.end(content);
      });
    });
  });

  server.listen(PORT, '0.0.0.0', () => {
    console.log(`📦 ApexStock Portfolio Native HTTP Server running at http://localhost:${PORT}`);
  });
}
