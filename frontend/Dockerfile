# SkyPath Frontend - Vite dev server with proxy to backend
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3030

ENV VITE_PROXY_TARGET=http://skypath-backend:9090
ENV VITE_OPEN_BROWSER=false
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
