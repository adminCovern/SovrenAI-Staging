# Sovren AI Frontend

## Overview
This is the production-ready frontend for Sovren AI, engineered for immediate deployment and robust integration with the MCP server and all backend services. It is high-performance, modular, secure, and CI/CD compatible.

## Features
- User and admin dashboards
- Voice interface (WebSocket, real-time)
- Shadow Board (virtual C-suite)
- Agent Battalion (AI agent management)
- Time Machine (predictive analytics)
- SOVREN Score (user analytics)
- Application review and user management (admin)
- System monitoring and telephony dashboards (admin)
- Secure JWT authentication and role-based access
- Robust error handling and security by default
- Unit test coverage for all major components and services

## Environment Variables
Set these in your deployment environment:

- `REACT_APP_API_URL` (default: `https://sovrenai.app/api`)
- `REACT_APP_WS_URL` (default: `wss://sovrenai.app/ws`)

## Deployment (Bare Metal)
1. **Install Node.js 18+ and npm 9+**
2. **Install dependencies:**
   ```sh
   npm install
   ```
3. **Build for production:**
   ```sh
   npm run build
   ```
4. **Serve the build directory with Nginx or Apache.**
   - Example Nginx config:
     - Set `root` to `/path/to/frontend/build`
     - Proxy `/api/` and `/ws/` to backend and MCP servers as needed
5. **Set environment variables in your system or via `.env` file.**

## Testing
- **Run all tests:**
  ```sh
  npm test
  ```
- **Lint and format:**
  ```sh
  npm run lint
  npm run format
  ```

## MCP and Backend Integration
- All API calls are routed through `src/services/api.js`.
- Real-time features (voice, MCP) use `src/services/websocket.js`.
- Ensure backend and MCP endpoints are reachable from the frontend server.

## Security
- All authentication is JWT-based; tokens are stored securely in localStorage.
- All API and WebSocket requests include the JWT for authorization.
- No secrets or credentials are hardcoded.

## CI/CD
- The project is compatible with all major CI/CD systems (GitHub Actions, GitLab CI, Jenkins, etc.).
- Run `npm install`, `npm run lint`, `npm test`, and `npm run build` in your pipeline.

---
**For mission-critical deployment, review all environment variables and server configurations.** 