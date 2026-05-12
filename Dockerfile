# Use Node.js 20 alpine as base image
FROM node:20-alpine

# Install build dependencies for node-canvas (required by qrcode library)
RUN apk add --no-cache python3 make g++ pixman-dev cairo-dev pango-dev jpeg-dev

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY src/ ./src/

# Set entrypoint
ENTRYPOINT ["node", "src/cli.js"]
