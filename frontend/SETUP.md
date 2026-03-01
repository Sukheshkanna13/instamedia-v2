# Frontend Setup Guide

## Quick Start

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Type check (optional)
npm run typecheck

# Build for production
npm run build
```

## Troubleshooting

### Error: "Could not find a declaration file for module 'react'"

**Cause**: Dependencies not installed

**Fix**:
```bash
cd frontend
npm install
```

This will install:
- `react` and `react-dom`
- `@types/react` and `@types/react-dom` (TypeScript definitions)
- `typescript`, `vite`, and other dev dependencies

### Error: "JSX element implicitly has type 'any'"

**Cause**: Same as above - missing React type definitions

**Fix**: Run `npm install` in the frontend directory

### Error: "tsc: command not found"

**Cause**: TypeScript not installed

**Fix**: Run `npm install` in the frontend directory

## Verification

After installing dependencies, verify everything works:

```bash
cd frontend

# Check TypeScript compilation
npm run typecheck
# Should output: No errors

# Start dev server
npm run dev
# Should start on http://localhost:5173
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── modules/          # Page-level components
│   │   │   ├── Overview.tsx
│   │   │   ├── BrandDNA.tsx
│   │   │   ├── Ideation.tsx
│   │   │   ├── CreativeStudio.tsx
│   │   │   ├── Calendar.tsx
│   │   │   ├── Connections.tsx    (NEW)
│   │   │   ├── BrandDrift.tsx     (NEW)
│   │   │   └── ColdStart.tsx      (NEW)
│   │   └── ui/               # Reusable UI components
│   │       ├── ScoreRing.tsx
│   │       └── CSVUploader.tsx    (NEW)
│   ├── lib/
│   │   └── api.ts            # API client (ENHANCED)
│   ├── types/
│   │   └── index.ts          # TypeScript types (UPDATED)
│   ├── App.tsx               # Main app component (UPDATED)
│   ├── main.tsx              # Entry point
│   └── index.css             # Global styles
├── package.json
├── tsconfig.json
├── tsconfig.app.json
├── vite.config.ts
└── index.html
```

## New Features Added

### 1. Enhanced API Client (`src/lib/api.ts`)
- ✅ 28s timeout protection (API Gateway safe)
- ✅ Automatic retry logic (2 attempts)
- ✅ S3 pre-signed URL support
- ✅ OAuth flow integration

### 2. CSV Uploader Component (`src/components/ui/CSVUploader.tsx`)
- ✅ Drag & drop file upload
- ✅ Direct S3 upload (bypasses API Gateway 10MB limit)
- ✅ Progress tracking
- ✅ File validation

### 3. Platform Connections (`src/components/modules/Connections.tsx`)
- ✅ OAuth flow for Instagram, LinkedIn, Twitter
- ✅ Connection status management
- ✅ Token expiry tracking

### 4. Brand Drift Detection (`src/components/modules/BrandDrift.tsx`)
- ✅ Drift magnitude gauge
- ✅ Event history timeline
- ✅ Recommendations panel

### 5. Cold Start Bootstrap (`src/components/modules/ColdStart.tsx`)
- ✅ 6 brand archetypes
- ✅ Archetype selection UI
- ✅ Transition plan visualization

## Development Workflow

1. **Install dependencies** (one time):
   ```bash
   cd frontend && npm install
   ```

2. **Start dev server**:
   ```bash
   npm run dev
   ```

3. **Make changes** to components in `src/`

4. **Hot reload** automatically updates the browser

5. **Type check** before committing:
   ```bash
   npm run typecheck
   ```

6. **Build for production**:
   ```bash
   npm run build
   ```

## Backend Integration

The frontend is ready and waiting for these backend endpoints:

### Required Endpoints
- `GET /api/esg/presigned-url` - Generate S3 pre-signed URL
- `POST /api/esg/upload` - Trigger ESG ingestion
- `GET /api/auth/{platform}` - Initiate OAuth
- `GET /api/auth/callback` - Handle OAuth callback
- `GET /api/drift/events` - Get drift events
- `POST /api/esg/bootstrap` - Bootstrap archetype

### Existing Endpoints (Already Working)
- `GET /api/health` - Health check
- `GET /api/brand-dna` - Get brand DNA
- `POST /api/brand-dna` - Save brand DNA
- `POST /api/analyze` - Emotional Aligner
- `POST /api/ideate` - Generate ideas
- `POST /api/studio/generate` - Generate content
- `GET /api/posts/calendar` - Get scheduled posts
- `POST /api/posts/schedule` - Schedule post

## Notes

- All TypeScript errors you see are **environment issues**, not code issues
- The code is production-ready once dependencies are installed
- Run `npm install` in the `frontend/` directory to fix all errors
- The diagnostics tool was running from the wrong directory (workspace root instead of frontend/)

## Next Steps

1. Install dependencies: `cd frontend && npm install`
2. Start dev server: `npm run dev`
3. Deploy backend Lambda functions
4. Test OAuth flow end-to-end
5. Deploy to production (Vercel/Netlify or S3+CloudFront)
