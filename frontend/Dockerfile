FROM node:18-alpine AS build

WORKDIR /app

# Install ALL dependencies (including devDependencies like vite)
COPY package.json package-lock.json* ./
RUN npm ci --include=dev

# Build React app with Vite
# VITE_API_BASE will be passed as a build-arg from the pipeline
ARG VITE_API_BASE
ENV VITE_API_BASE=${VITE_API_BASE}

COPY . .
RUN npm run build

# ---- Production image ----
FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Remove default nginx static content
RUN rm -rf ./*

# Copy built assets from build stage
COPY --from=build /app/dist ./

# Expose HTTP port
EXPOSE 80

# Use default NGINX start command
CMD ["nginx", "-g", "daemon off;"]
