FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json angular.json tsconfig*.json ./
COPY src ./src
RUN npm ci --no-audit --no-fund && npm run build
FROM nginx:alpine
COPY --from=build /app/dist/stockflow/browser /usr/share/nginx/html
EXPOSE 80
