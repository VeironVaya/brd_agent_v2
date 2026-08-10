import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage.jsx'
import ConversationsPage from './pages/ConversationsPage.jsx'
import DraftSessionPage from './pages/DraftSessionPage.jsx'
import ExportPage from './pages/ExportPage.jsx'
import { getToken } from './services/api.js'

function RequireAuth({ children }) {
  if (!getToken()) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
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
