FROM node:22-bookworm AS build
WORKDIR /app
COPY admin-web/package.json admin-web/package-lock.json* ./
RUN npm ci --no-audit --no-fund
COPY admin-web/ ./
RUN npm run build

FROM nginx:1.28.0-alpine
COPY deploy/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
