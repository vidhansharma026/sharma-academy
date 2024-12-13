# Use a lightweight Node.js image
FROM node:18.20.5-alpine

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the application files
COPY . .

# Expose the port on which the React app runs
EXPOSE 3000

# Start the React development server
CMD ["npm", "start"]
