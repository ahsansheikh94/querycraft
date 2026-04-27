import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

// Pages
import LoginPage from './pages/auth/LoginPage';
import SignupPage from './pages/auth/SignupPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import ProjectsPage from './pages/project/ProjectsPage';
import CreateProjectPage from './pages/project/CreateProjectPage';
import ProjectDetailPage from './pages/project/ProjectDetailPage';
import SchemaPage from './pages/project/SchemaPage';
import QueryPage from './pages/project/QueryPage';

// Store
import { useAuthStore } from './store/auth';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user, getCurrentUser } = useAuthStore();

  useEffect(() => {
    if (!user && isAuthenticated) {
      getCurrentUser();
    }
  }, [user, isAuthenticated, getCurrentUser]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Public Route Component (redirects to dashboard if authenticated)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-background flex flex-col">
          <div
            role="status"
            className="shrink-0 border-b border-primary/20 bg-primary px-3 py-2 text-center text-xs leading-snug text-primary-foreground sm:text-sm"
          >
            You might experience a delay in your first request as the backend of
            this project is hosted on a free service that gets down after 15
            minutes of inactivity. Thank you for your patience, amigo!
          </div>
          <div className="min-h-0 flex-1">
            <AnimatePresence mode="wait">
              <Routes>
                {/* Public Routes */}
                <Route
                  path="/login"
                  element={
                    <PublicRoute>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        <LoginPage />
                      </motion.div>
                    </PublicRoute>
                  }
                />
                <Route
                  path="/signup"
                  element={
                    <PublicRoute>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        <SignupPage />
                      </motion.div>
                    </PublicRoute>
                  }
                />

                {/* Protected Routes */}
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        <DashboardPage />
                      </motion.div>
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/projects"
                  element={
                    <ProtectedRoute>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        <ProjectsPage />
                      </motion.div>
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/projects/new"
                  element={
                    <ProtectedRoute>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        <CreateProjectPage />
                      </motion.div>
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/project/:id"
                  element={
                    <ProtectedRoute>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        <ProjectDetailPage />
                      </motion.div>
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/project/:id/schema"
                  element={
                    <ProtectedRoute>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        <SchemaPage />
                      </motion.div>
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/project/:id/query"
                  element={
                    <ProtectedRoute>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        <QueryPage />
                      </motion.div>
                    </ProtectedRoute>
                  }
                />

                {/* Default redirect */}
                <Route
                  path="/"
                  element={<Navigate to="/dashboard" replace />}
                />

                {/* Catch all route - redirect to dashboard for authenticated users */}
                <Route
                  path="*"
                  element={
                    <ProtectedRoute>
                      <Navigate to="/dashboard" replace />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </AnimatePresence>
          </div>
        </div>

        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'hsl(var(--card))',
              color: 'hsl(var(--card-foreground))',
              border: '1px solid hsl(var(--border))',
            },
            success: {
              iconTheme: {
                primary: 'hsl(var(--primary))',
                secondary: 'hsl(var(--primary-foreground))',
              },
            },
            error: {
              iconTheme: {
                primary: 'hsl(var(--destructive))',
                secondary: 'hsl(var(--destructive-foreground))',
              },
            },
          }}
        />
      </Router>
    </QueryClientProvider>
  );
}

export default App;
