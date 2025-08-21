# QueryCraft Frontend

A modern, responsive React frontend for the SQL Query Generator application. Built with TypeScript, Tailwind CSS, and shadcn/ui components.

## Features

### 🎨 Modern UI Design

- **Dark Theme**: Beautiful dark mode with glass morphism effects
- **Responsive Design**: Mobile-first approach with responsive layouts
- **Animations**: Smooth transitions and micro-interactions with Framer Motion
- **Glass Morphism**: Subtle glass effects on cards and modals
- **Gradient Accents**: Modern gradient text and button effects

### 🔐 Authentication System

- **Login/Signup**: Modern authentication forms with validation
- **JWT Integration**: Secure token-based authentication
- **Protected Routes**: Route guards for authenticated users
- **User Management**: Profile management and session handling

### 📊 Dashboard

- **Project Overview**: Visual project grid with statistics
- **Recent Queries**: Quick access to recent query history
- **Search & Filter**: Real-time search functionality
- **Empty States**: Beautiful empty states for new users

### 🗄️ Project Management

- **Project Cards**: Visual project representation
- **Create/Edit**: Modal forms for project management
- **Statistics**: Project metrics and analytics
- **Navigation**: Intuitive project navigation

## Technology Stack

- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS with custom dark theme
- **UI Components**: shadcn/ui component library
- **State Management**: Zustand with persistence
- **API Integration**: TanStack Query (React Query)
- **Routing**: React Router v6
- **Forms**: React Hook Form with Zod validation
- **Animations**: Framer Motion
- **Notifications**: React Hot Toast
- **Icons**: Lucide React
- **Build Tool**: Vite

## Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running (see server README)

## Installation

1. **Clone the repository**

   ```bash
   cd web
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:

   ```env
   VITE_API_URL=http://localhost:5000/api
   ```

4. **Start the development server**

   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173`

## Project Structure

```
src/
├── components/
│   ├── ui/                 # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── layout/            # Layout components
│   │   └── Header.tsx
│   ├── auth/              # Authentication components
│   ├── project/           # Project-related components
│   └── query/             # Query-related components
├── pages/
│   ├── auth/              # Authentication pages
│   │   ├── LoginPage.tsx
│   │   └── SignupPage.tsx
│   ├── dashboard/         # Dashboard pages
│   │   └── DashboardPage.tsx
│   └── project/           # Project pages
├── store/                 # Zustand stores
│   └── auth.ts
├── lib/                   # Utilities and services
│   ├── api.ts            # API service
│   └── utils.ts          # Utility functions
├── types/                 # TypeScript interfaces
│   └── index.ts
├── hooks/                 # Custom React hooks
└── App.tsx               # Main application component
```

## Key Components

### Authentication

- **LoginPage**: User login with email/password
- **SignupPage**: User registration with validation
- **ProtectedRoute**: Route guard for authenticated users

### Dashboard

- **DashboardPage**: Main dashboard with projects and recent queries
- **Header**: Navigation header with user menu
- **ProjectCard**: Visual project representation

### UI Components

- **Button**: Reusable button with multiple variants
- **Card**: Glass morphism card components
- **Input**: Form input with validation states
- **Textarea**: Multi-line text input

## API Integration

The frontend integrates with the backend API through the `apiService` in `src/lib/api.ts`. Key features:

- **Automatic Token Management**: JWT tokens are automatically included in requests
- **Error Handling**: Centralized error handling with toast notifications
- **Request/Response Interceptors**: Automatic token refresh and error handling
- **Type Safety**: Full TypeScript support for API responses

## Styling

### Tailwind CSS Configuration

- **Custom Theme**: Dark mode with custom color palette
- **Glass Morphism**: Custom glass effect utilities
- **Gradients**: Custom gradient text and button styles
- **Animations**: Custom animation utilities

### CSS Classes

```css
.glass-card          /* Glass morphism card effect */
/* Glass morphism card effect */
.gradient-text       /* Gradient text effect */
.gradient-border; /* Gradient border effect */
```

## State Management

### Zustand Stores

- **Auth Store**: User authentication state and actions
- **Persistent Storage**: Authentication state persists across sessions

### React Query

- **API Caching**: Automatic caching of API responses
- **Background Updates**: Automatic data refetching
- **Optimistic Updates**: Immediate UI updates with background sync

## Form Handling

### React Hook Form + Zod

- **Type Safety**: Full TypeScript support
- **Validation**: Schema-based validation with Zod
- **Performance**: Optimized re-renders and validation

## Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Code Quality

- **ESLint**: Code linting with TypeScript support
- **Prettier**: Code formatting
- **TypeScript**: Strict type checking

## Environment Variables

| Variable       | Description     | Default                     |
| -------------- | --------------- | --------------------------- |
| `VITE_API_URL` | Backend API URL | `http://localhost:5000/api` |

## Deployment

### Build for Production

```bash
npm run build
```

### Deploy to Vercel

1. Connect your repository to Vercel
2. Set environment variables
3. Deploy automatically on push

### Deploy to Netlify

1. Connect your repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `dist`

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:

1. Check the documentation
2. Review the console for errors
3. Ensure the backend API is running
4. Create an issue in the repository
