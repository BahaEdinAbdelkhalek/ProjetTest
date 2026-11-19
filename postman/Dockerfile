FROM node:22-alpine
WORKDIR /tests
RUN npm install --no-audit --no-fund newman@6.2.1
COPY StockFlow.postman_collection.json ./collection.json
ENTRYPOINT ["./node_modules/.bin/newman","run","collection.json"]
