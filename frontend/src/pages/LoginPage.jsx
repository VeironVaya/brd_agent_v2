import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Logo from '../components/common/Logo.jsx'
import Button from '../components/common/Button.jsx'
import * as api from '../services/api.js'

export default function LoginPage() {
  const navigate = useNavigate()
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit() {
    setError('')
    if (!email.trim() || !password) {
      setError('Enter your email and password to continue.')
      return
    }
    if (mode === 'register' && !name.trim()) {
      setError('Enter your name to create an account.')
      return
    }

    setSubmitting(true)
    try {
      if (mode === 'register') {
        await api.register({ email: email.trim(), password, name: name.trim() })
      } else {
        await api.login({ email: email.trim(), password })
      }
      navigate('/')
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="w-full min-h-screen bg-white flex items-center justify-center p-6">
      <div className="w-full max-w-105 flex flex-col items-center">
        <div className="mb-6">
          <Logo size={44} />
        </div>
        <div className="text-[26px] font-bold text-center">
          {mode === 'login' ? 'Sign in to BRD-Agent' : 'Create your BRD-Agent account'}
        </div>
        <div className="text-[15px] text-text-secondary mt-2 text-center leading-relaxed">
          Use your work email to continue tracking Business Requirement Documents.
        </div>

        <div className="w-full flex flex-col gap-3.5 mt-8">
          {mode === 'register' && (
            <div className="flex flex-col gap-1.5">
              <label className="text-[13px] font-semibold">Name</label>
              <input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) => {
                  setName(e.target.value)
                  setError('')
                }}
                className="h-13 bg-white font-[inherit] rounded-btn px-4 text-base text-text-primary outline-none border border-border focus:border-text-primary"
              />
            </div>
          )}

          <div className="flex flex-col gap-1.5">
            <label className="text-[13px] font-semibold">Work email</label>
            <input
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                setError('')
              }}
              className="h-13 bg-white font-[inherit] rounded-btn px-4 text-base text-text-primary outline-none border border-border focus:border-text-primary"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[13px] font-semibold">Password</label>
            <input
              type="password"
              placeholder={mode === 'register' ? 'At least 8 characters' : 'Your password'}
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                setError('')
              }}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
              className={`h-13 bg-white font-[inherit] rounded-btn px-4 text-base text-text-primary outline-none ${
                error ? 'border-[1.5px] border-confidence-low' : 'border border-border focus:border-text-primary'
              }`}
            />
            {error && <div className="text-[12.5px] text-confidence-low leading-snug">{error}</div>}
          </div>

          <Button variant="primary" size="lg" className="mt-1.5 w-full" onClick={handleSubmit} disabled={submitting}>
            {mode === 'login' ? 'Sign in' : 'Create account'}
          </Button>
        </div>

        <div className="text-[13px] text-text-tertiary mt-7 text-center">
          {mode === 'login' ? (
            <>
              New here?{' '}
              <button
                type="button"
                onClick={() => {
                  setMode('register')
                  setError('')
                }}
                className="text-text-primary font-semibold underline bg-transparent border-none cursor-pointer p-0"
              >
                Create an account
              </button>
              .
            </>
          ) : (
            <>
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => {
                  setMode('login')
                  setError('')
                }}
                className="text-text-primary font-semibold underline bg-transparent border-none cursor-pointer p-0"
              >
                Sign in
              </button>
              .
            </>
          )}
        </div>
      </div>
    </div>
  )
}
