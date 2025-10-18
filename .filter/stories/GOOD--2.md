# GOOD--2: Setup TypeScript/Vite frontend with Python backend integration

**Created:** 2025-10-18T05:19:40.683597+00:00
**Status:** Planning

## Description

Configure full-stack development environment: Vite dev server with HMR for frontend development, Python server for API endpoints and static file serving, with proper proxy configuration

## Acceptance Criteria

### Frontend Setup

- [ ] Vite project initialized with TypeScript configuration
- [ ] Basic "Hello World" page renders in browser
- [ ] Hot module replacement (HMR) works - changes reflect without full reload
- [ ] TypeScript compilation with strict mode enabled
- [ ] ESLint configured for TypeScript best practices
- [ ] Frontend build output goes to `dist/` directory

### Backend Integration

- [ ] Python server serves static files from Vite build output
- [ ] Python server provides at least one test API endpoint (e.g., `/api/health`)
- [ ] Vite dev server proxies `/api/*` requests to Python backend during development
- [ ] CORS configured properly for local development

### Development Workflow

- [ ] Single command starts both dev servers (or documented separate commands)
- [ ] Frontend can make API calls to backend in dev mode
- [ ] Production build creates optimized static files
- [ ] Python server can serve production build

### Testing

- [ ] Frontend test framework configured (Vitest recommended)
- [ ] At least one basic frontend test passes
- [ ] Backend test setup verified (pytest already configured)
- [ ] At least one basic backend API test passes

### Documentation

- [ ] README updated with setup instructions
- [ ] Development vs production mode documented
- [ ] Environment variables documented (if needed)

## Implementation Notes

### Architecture

- **Development Mode:**

  - Vite dev server (default port 5173) with HMR
  - Python server (e.g., port 8000) for API endpoints
  - Vite proxy forwards `/api/*` to Python backend

- **Production Mode:**

  - Vite builds optimized static files to `dist/`
  - Python server serves static files AND API endpoints
  - Single deployment artifact

### Technology Stack

- **Frontend:** TypeScript + Vite + React (or vanilla TS if preferred)
- **Backend:** Python with FastAPI or Flask for API endpoints
- **Testing:** Vitest for frontend, pytest for backend
- **Build:** Vite build → dist/ → served by Python

### File Structure

```
good-neighbor/
├── src/
│   └── good_neighbor/          # Python backend
│       ├── __init__.py
│       ├── server.py           # FastAPI/Flask app
│       └── api/                # API endpoints
├── frontend/                   # Vite + TypeScript
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.tsx (or .ts)
│   │   └── components/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
├── dist/                       # Vite build output (gitignored)
├── tests/                      # Python tests
├── pyproject.toml
└── README.md
```

### Key Configuration Files

**vite.config.ts:**

```typescript
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: '../dist',
  },
})
```

**Python server setup:**

- Use FastAPI for modern async API framework
- Serve static files from `dist/` in production
- Provide `/api/health` endpoint for testing
- Set up CORS middleware for development

### Testing Strategy

- **Frontend:** Basic smoke test that app renders
- **Backend:** Test health endpoint returns 200
- No extensive testing needed yet - just verify the setup works

### Dependencies to Add

**Frontend (package.json):**

- vite
- typescript
- @vitejs/plugin-react (if using React)
- vitest (for testing)
- eslint + typescript-eslint

**Backend (pyproject.toml):**

- fastapi
- uvicorn (ASGI server)
- python-multipart (for forms)

## Testing Notes

### Manual Testing Checklist

1. Start dev servers
1. Open http://localhost:5173 - see "Hello World"
1. Edit frontend code - verify HMR updates
1. Call `/api/health` from frontend - verify response
1. Run `npm run build` - verify dist/ created
1. Run Python server in production mode - verify static files served
1. Run frontend tests - verify passing
1. Run backend tests - verify passing

### Edge Cases

- Handle CORS in development mode
- Ensure static file routing doesn't conflict with API routes
- Verify HMR works with TypeScript files
- Test that production build is optimized (tree-shaking, minification)

## Notes

This story establishes the foundation for all future development. Getting this right means:

- Fast development iteration with HMR
- Type safety with TypeScript
- Clean separation between frontend and backend
- Easy deployment story (build frontend, deploy Python server)

Future stories will build on this setup to add:

- OAuth authentication
- Widget management API
- User preferences storage
- Link click tracking
- Custom widgets and iframe support

## Related Issues

This is the foundational story for the good-neighbor project architecture.
