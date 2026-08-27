import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext.jsx'
import LoginPage from './pages/LoginPage.jsx'
import ConversationsPage from './pages/ConversationsPage.jsx'
import DraftSessionPage from './pages/DraftSessionPage.jsx'
import ExportPage from './pages/ExportPage.jsx'

/**
 * RequireAuth — validates auth against the server (via AuthContext) before
 * rendering protected routes. Three states:
 *   loading  → render nothing (blank) while GET /auth/session is in-flight.
 *              Never redirect during this window — a valid token would
 *              incorrectly bounce the user to /login on every hard refresh.
 *   no user  → redirect to /login.
 *   user ok  → render children.
 */
function RequireAuth({ children }) {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  return children
}

/**
 * RequireGuest — the inverse of RequireAuth. Protects the login page
 * from authenticated users, instantly redirecting them to the dashboard.
 */
function RequireGuest({ children }) {
  const { user, loading } = useAuth()
  if (loading) return null
  if (user) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route 
        path="/login" 
        element={
          <RequireGuest>
            <LoginPage />
          </RequireGuest>
        } 
      />
      <Route
        path="/"
        element={
          <RequireAuth>
            <ConversationsPage />
          </RequireAuth>
        }
      />
      <Route path="/conversations" element={<Navigate to="/" replace />} />
      <Route
        path="/conversations/:id"
        element={
          <RequireAuth>
            <DraftSessionPage />
          </RequireAuth>
        }
      />
      <Route
        path="/conversations/:id/export"
        element={
          <RequireAuth>
            <ExportPage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

