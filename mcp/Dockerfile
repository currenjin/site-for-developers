FROM node:22-bookworm-slim
WORKDIR /app
COPY mcp/package.json mcp/package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts && npm cache clean --force
COPY mcp/src ./src
COPY mcp/catalog.json mcp/README.md mcp/LICENSE ./
USER node
ENV MCP_HOST=0.0.0.0 PORT=3000
EXPOSE 3000
# Explicit MCP_ALLOWED_HOSTS / MCP_ALLOWED_ORIGINS must be provided at runtime.
CMD ["node", "src/cli.js", "--http"]
