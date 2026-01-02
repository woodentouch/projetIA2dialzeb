FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
# Use npm ci when package-lock.json exists, otherwise fallback to npm install
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm i -g serve
COPY --from=build /app/dist ./dist
CMD ["serve", "-s", "dist", "-l", "3000"]
