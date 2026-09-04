# --- Build stage: compile the Vite/React SPA into static assets ---
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# VITE_API_BASE_URL is baked into the JS bundle at build time. In
# production nginx serves the SPA and proxies /api, /auth, /health to the
# backend container on the SAME origin — so this stays empty (relative
# fetch("" + path) == same-origin request), which sidesteps CORS entirely
# instead of needing a real backend URL.
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

# --- Runtime stage: serve the built static files with nginx ---
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
