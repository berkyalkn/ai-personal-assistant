    FROM node:18-alpine AS builder

    WORKDIR /app

    COPY package.json package-lock.json ./
    RUN npm ci
    
    COPY . .

    ARG NEXT_PUBLIC_API_URL 
    ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
    
    RUN npm run build
    
    
    FROM nginxinc/nginx-unprivileged:alpine-slim
    
    COPY nginx.conf /etc/nginx/conf.d/default.conf
    
    COPY --from=builder /app/out /usr/share/nginx/html
    
    USER root
    RUN chgrp -R 0 /usr/share/nginx/html && \
        chmod -R g=u /usr/share/nginx/html
    USER 101
    
    EXPOSE 8080
    
    CMD ["nginx", "-g", "daemon off;"]