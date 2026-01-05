# === Frontend Dockerfile (Angular) ===
# Multi-stage: build Angular app then serve with Nginx

# --- Build Stage ---
FROM node:20-alpine AS build
WORKDIR /app
ENV CI=true
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps --no-audit --no-fund
COPY . .
RUN npm run build --if-present && ls -lah dist

# --- Runtime Stage ---
FROM nginx:1.27-alpine AS runtime
WORKDIR /usr/share/nginx/html
# Remove default Nginx static content
RUN rm -rf ./*
# Copy compiled Angular output (Angular 20 uses dist/front-end)
COPY --from=build /app/dist/front-end/browser ./
# Custom Nginx config for SPA & caching
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD wget -qO- http://localhost/ || exit 1

# Use non-root where feasible (nginx already runs as nginx user on alpine image)
