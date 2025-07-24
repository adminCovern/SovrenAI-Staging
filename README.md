# 🚀 Sovren AI - Complete Executive Command Center

A production-grade, holographic command bridge for AI executives with real-time 3D visualization, distributed consensus, and enterprise-grade security.

## 📁 Workspace Structure

```
sovren-ai-workspace/
├── frontend/                 # Next.js 14 Frontend Application
│   ├── src/
│   │   ├── app/             # Next.js App Router
│   │   ├── components/      # React & Three.js Components
│   │   ├── services/        # Core Business Logic
│   │   ├── store/           # Redux State Management
│   │   ├── integrations/    # External System Integrations
│   │   └── types/           # TypeScript Type Definitions
│   └── package.json
├── backend/                  # Python Backend Application
│   ├── api/                 # FastAPI REST API
│   ├── core/                # Core Business Logic
│   ├── consciousness/       # AI Consciousness Engine
│   ├── database/            # Database Models & Migrations
│   ├── voice/               # Voice Integration Services
│   └── requirements.txt
├── shared/                  # Shared Types & Utilities
│   ├── src/
│   │   ├── types/           # Shared TypeScript Types
│   │   ├── utils/           # Shared Utilities
│   │   └── constants.ts     # Shared Constants
│   └── package.json
└── package.json             # Root Workspace Configuration
```

## 🎯 Key Features

### Frontend (Next.js 14 + Three.js)
- **Real-time 3D Visualization**: Holographic executive avatars with Three.js
- **Distributed Consensus**: RAFT protocol implementation for fault tolerance
- **Enterprise Security**: XSS protection, CSRF tokens, input validation
- **Performance Optimization**: Adaptive quality settings, memory management
- **Error Recovery**: Automatic recovery mechanisms for critical failures
- **Comprehensive Testing**: 80%+ test coverage with unit and integration tests

### Backend (Python + FastAPI)
- **AI Consciousness Engine**: Advanced AI decision-making capabilities
- **Voice Integration**: FreeSwitch PBX integration for voice communications
- **Database Management**: PostgreSQL with advanced query optimization
- **API Gateway**: RESTful API with OpenAPI documentation
- **Security Hardening**: Quantum-resistant encryption and authentication
- **Performance Monitoring**: Real-time system metrics and alerting

### Shared Components
- **Type Safety**: Shared TypeScript types for frontend-backend consistency
- **Validation**: Zod-based validation schemas
- **Encryption**: Quantum-resistant cryptographic utilities
- **WebSocket**: Real-time communication protocols
- **Constants**: Shared configuration and constants

## 🛠️ Installation & Setup

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.12+** and pip
- **PostgreSQL 14+**
- **Modern browser** with WebGL support

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/sovren-ai-workspace.git
cd sovren-ai-workspace

# Install all dependencies
npm run install:all

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development servers
npm run dev
```

### Development Commands

```bash
# Start both frontend and backend in development mode
npm run dev

# Start only frontend
npm run dev:frontend

# Start only backend
npm run dev:backend

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint

# Start production servers
npm start
```

## 🏗️ Architecture Overview

### Frontend Architecture
- **Next.js 14**: App Router with TypeScript
- **Three.js**: WebGL 2.0 3D rendering
- **Redux Toolkit**: State management with real-time sync
- **WebSocket**: Real-time communication with backend
- **OAuth2**: Secure authentication flows

### Backend Architecture
- **FastAPI**: High-performance REST API
- **PostgreSQL**: Primary database with advanced indexing
- **Redis**: Caching and session management
- **WebSocket**: Real-time bidirectional communication
- **AI Engine**: Consciousness and decision-making algorithms

### Shared Architecture
- **TypeScript**: Type-safe shared interfaces
- **Zod**: Runtime validation schemas
- **Quantum Security**: Post-quantum cryptographic protection
- **RAFT Consensus**: Distributed state management

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://localhost:5432/sovren_ai
REDIS_URL=redis://localhost:6379

# API Configuration
API_BASE_URL=http://localhost:3000
WEBSOCKET_URL=ws://localhost:3001

# Security
JWT_SECRET=your-jwt-secret
QUANTUM_KEY=your-quantum-key

# External Integrations
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
```

### Database Setup

```bash
# Create PostgreSQL database
createdb sovren_ai

# Run database migrations
cd backend
python -m alembic upgrade head
```

## 🚀 Production Deployment

### Frontend Deployment

```bash
# Build frontend for production
npm run build:frontend

# Deploy to Vercel/Netlify
npm run deploy:frontend
```

### Backend Deployment

```bash
# Build backend for production
npm run build:backend

# Deploy to bare metal server
npm run deploy:backend
```

### Complete Production Setup

```bash
# Install production dependencies
npm run install:production

# Build all packages
npm run build

# Start production servers
npm start
```

## 🧪 Testing

### Frontend Tests

```bash
# Run frontend tests
npm run test:frontend

# Run with coverage
npm run test:frontend:coverage
```

### Backend Tests

```bash
# Run backend tests
npm run test:backend

# Run with coverage
npm run test:backend:coverage
```

### Integration Tests

```bash
# Run integration tests
npm run test:integration
```

## 📊 Performance Monitoring

### Frontend Metrics
- **Frame Rate**: Target 120 FPS for 3D rendering
- **Memory Usage**: GPU memory optimization
- **Load Time**: Sub-2 second initial load
- **WebSocket Latency**: Sub-100ms real-time updates

### Backend Metrics
- **API Response Time**: Sub-50ms average
- **Database Query Performance**: Optimized with indexes
- **Memory Usage**: Efficient garbage collection
- **CPU Utilization**: Load balancing across cores

## 🔒 Security Features

### Frontend Security
- **XSS Protection**: Content Security Policy
- **CSRF Protection**: Token-based validation
- **Input Validation**: Zod schema validation
- **Secure Headers**: Helmet.js configuration

### Backend Security
- **Quantum-Resistant Encryption**: Post-quantum cryptography
- **JWT Authentication**: Secure token management
- **Rate Limiting**: DDoS protection
- **SQL Injection Prevention**: Parameterized queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- **Documentation**: [docs.sovren.ai](https://docs.sovren.ai)
- **Issues**: [GitHub Issues](https://github.com/your-org/sovren-ai-workspace/issues)
- **Discord**: [Sovren AI Community](https://discord.gg/sovren-ai)

---

**Built with ❤️ by the Sovren AI Team** 