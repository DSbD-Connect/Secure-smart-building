FROM node:20.15.1 as build

# Build stage
WORKDIR /app

COPY client/package*.json ./

RUN npm install

COPY client/ .

RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the Nginx configuration
COPY client/nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built app to Nginx serve directory
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]




