# Use official Node.js image
FROM node:20-alpine

# Set work directory
WORKDIR /app

# Configure npm
RUN npm config set registry https://registry.npmjs.org/ && \
    npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy project files
COPY . .

# Expose port for Next.js
EXPOSE 3000

# Start Next.js app
CMD ["npm", "run", "dev"] 