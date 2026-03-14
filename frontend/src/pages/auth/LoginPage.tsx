import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react'
import apiClient from '@/api/client'
import { useAuthStore } from '@/store/authStore'

const schema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
})
type Form = z.infer<typeof schema>

export default function LoginPage() {
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuthStore()
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/'

  const { register, handleSubmit, formState: { errors } } = useForm<Form>({
    resolver: zodResolver(schema),
  })

  const clearAlerts = () => { setErrorMsg(null); setSuccessMsg(null) }

  const onSubmit = async (data: Form) => {
    setLoading(true)
    clearAlerts()
    try {
      const res = await apiClient.post('/api/auth/login', data, {
        params: { _t: Date.now() },   // cache-bust to prevent 304
      })
      const { access_token, refresh_token, user } = res.data
      login(user, access_token, refresh_token)
      setSuccessMsg(`Welcome back, ${user.full_name || user.username}!`)
      setTimeout(() => navigate(from, { replace: true }), 600)
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string }; status?: number }; message?: string }
      if (e.response?.data?.detail) {
        setErrorMsg(e.response.data.detail)
      } else if (e.message?.includes('Network Error') || e.message?.includes('ERR_CONNECTION_REFUSED')) {
        setErrorMsg('Cannot connect to server. Make sure the backend is running on port 8000.')
      } else {
        setErrorMsg(e.message || 'An unexpected error occurred. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const runDiagnostics = async () => {
    clearAlerts()
    setLoading(true)
    try {
      const res = await apiClient.get('/api/auth/health')
      const d = res.data
      const msgs: string[] = []
      msgs.push(d.snowflake_connection ? '\u2713 Snowflake connected' : '\u2717 Snowflake NOT connected')
      msgs.push(d.database_exists ? '\u2713 Database found' : '\u2717 Database missing')
      msgs.push(d.auth_schema ? '\u2713 AUTH schema found' : '\u2717 AUTH schema missing')
      msgs.push(d.users_table ? '\u2713 USERS table found' : '\u2717 USERS table missing')
      msgs.push(d.admin_user ? '\u2713 Admin user exists' : '\u2717 Admin user missing')
      if (d.details?.length) {
        msgs.push('\u2014')
        d.details.forEach((s: string) => msgs.push(s))
      }
      const allGood = d.snowflake_connection && d.database_exists && d.auth_schema && d.users_table && d.admin_user
      if (allGood && d.details?.some((s: string) => s.includes('VALID'))) {
        setSuccessMsg(msgs.join('\n'))
      } else {
        setErrorMsg(msgs.join('\n'))
      }
    } catch (err: unknown) {
      setErrorMsg('Cannot reach backend at http://localhost:8000\n\nMake sure the API server is running.\nRun start.bat or start the backend manually.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center relative overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #0a1628 0%, #0d2444 40%, #0f3566 70%, #1a4d8f 100%)' }}
    >
      {/* Background blobs */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full opacity-20"
             style={{ background: 'radial-gradient(circle, #007AFF, transparent)' }} />
        <div className="absolute -bottom-32 -left-32 w-80 h-80 rounded-full opacity-15"
             style={{ background: 'radial-gradient(circle, #5856D6, transparent)' }} />
        <div className="absolute top-1/2 left-1/4 w-64 h-64 rounded-full opacity-10"
             style={{ background: 'radial-gradient(circle, #30B0C7, transparent)' }} />
      </div>

      {/* Grid dots */}
      <div className="absolute inset-0 opacity-5"
           style={{ backgroundImage: 'radial-gradient(circle, #ffffff 1px, transparent 1px)', backgroundSize: '32px 32px' }} />

      {/* Content */}
      <div className="relative z-10 w-full max-w-sm mx-4">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 shadow-xl"
               style={{ background: 'linear-gradient(135deg, #007AFF, #0055D0)' }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"
                 strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8h1a4 4 0 010 8h-1" />
              <path d="M2 8h16v9a4 4 0 01-4 4H6a4 4 0 01-4-4V8z" />
              <line x1="6" y1="1" x2="6" y2="4" />
              <line x1="10" y1="1" x2="10" y2="4" />
              <line x1="14" y1="1" x2="14" y2="4" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">CargoZen</h1>
          <p className="text-sm mt-1" style={{ color: 'rgba(255,255,255,0.5)' }}>
            Freight Management System
          </p>
        </div>

        {/* ──── Login Card ──── */}
        <div className="rounded-2xl p-8 shadow-xl border"
             style={{ background: 'rgba(255,255,255,0.97)', borderColor: 'rgba(255,255,255,0.2)' }}>

          <h2 className="text-lg font-semibold text-[#1C1C1E] mb-5">Sign in to your account</h2>

          {/* ── INLINE ERROR BOX ── */}
          {errorMsg && (
            <div className="mb-4 flex items-start gap-3 rounded-xl px-4 py-3"
                 style={{ background: '#FFF2F0', border: '1px solid #FFDAD6' }}>
              <AlertCircle size={18} className="shrink-0 mt-0.5" style={{ color: '#FF3B30' }} />
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-xs mb-0.5" style={{ color: '#FF3B30' }}>Sign in failed</p>
                <p className="text-xs leading-relaxed whitespace-pre-line" style={{ color: '#6B1A16' }}>
                  {errorMsg}
                </p>
              </div>
            </div>
          )}

          {/* ── INLINE SUCCESS BOX ── */}
          {successMsg && (
            <div className="mb-4 flex items-start gap-3 rounded-xl px-4 py-3"
                 style={{ background: '#F0FFF4', border: '1px solid #C6F6D5' }}>
              <CheckCircle size={18} className="shrink-0 mt-0.5" style={{ color: '#34C759' }} />
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-xs mb-0.5" style={{ color: '#34C759' }}>Success</p>
                <p className="text-xs leading-relaxed whitespace-pre-line" style={{ color: '#1A4A2E' }}>
                  {successMsg}
                </p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Username */}
            <div>
              <label className="label">Username</label>
              <input
                className={`input ${errors.username ? 'border-ios-red focus:ring-ios-red/20' : ''}`}
                placeholder="Enter your username"
                autoComplete="username"
                autoFocus
                {...register('username', { onChange: clearAlerts })}
              />
              {errors.username && (
                <p className="mt-1 text-2xs font-medium" style={{ color: '#FF3B30' }}>
                  {errors.username.message}
                </p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="label">Password</label>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  className={`input pr-11 ${errors.password ? 'border-ios-red focus:ring-ios-red/20' : ''}`}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  {...register('password', { onChange: clearAlerts })}
                />
                <button
                  type="button"
                  onClick={() => setShowPass(s => !s)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-ios-gray2 hover:text-ios-gray transition-colors"
                >
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-2xs font-medium" style={{ color: '#FF3B30' }}>
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 text-white py-3 text-base font-semibold mt-2 rounded-xl shadow-sm transition-all active:scale-95 disabled:opacity-50"
              style={{ background: loading ? '#60a5fa' : 'linear-gradient(135deg, #007AFF, #0055D0)' }}
            >
              {loading ? (
                <>
                  <svg className="w-4 h-4 spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Signing in&hellip;
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <p className="mt-5 text-center text-xs text-ios-gray2">
            Default:{' '}
            <span className="font-mono font-medium text-ios-gray">admin</span> /{' '}
            <span className="font-mono font-medium text-ios-gray">Admin@123</span>
          </p>
        </div>

        {/* ── Diagnostics button ── */}
        <div className="mt-4 text-center">
          <button
            type="button"
            onClick={runDiagnostics}
            disabled={loading}
            className="text-xs font-medium hover:underline transition-colors"
            style={{ color: 'rgba(255,255,255,0.5)' }}
          >
            Connection issues? Run diagnostics
          </button>
        </div>

        <p className="text-center mt-4 text-2xs" style={{ color: 'rgba(255,255,255,0.3)' }}>
          &copy; {new Date().getFullYear()} CargoZen Logistics. All rights reserved.
        </p>
      </div>
    </div>
  )
}