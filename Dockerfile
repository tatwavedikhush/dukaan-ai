FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json .nvmrc ./
COPY public ./public
COPY server.js ./server.js
COPY test ./test
ENV NODE_ENV=production PORT=3000
EXPOSE 3000
CMD ["npm", "start"]
