FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Build the app
RUN npm run build

# Install a simple server to serve the static files
RUN npm install -g serve

EXPOSE 3000

# Serve the app
CMD ["serve", "-s", "dist", "-l", "3000"] 