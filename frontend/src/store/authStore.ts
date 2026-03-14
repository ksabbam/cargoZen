import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'

interface AuthStore {
  user: User | null
  access_token: string | null
  refresh_token: string | null
  isAuthenticated: boolean
  login: (user: User, access_token: string, refresh_token: string) => void
  logout: () => void
  setTokens: (access_token: string) => void
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      access_token: null,
      refresh_token: null,
      isAuthenticated: false,

      login: (user, access_token, refresh_token) =>
        set({ user, access_token, refresh_token, isAuthenticated: true }),

      logout: () =>
        set({ user: null, access_token: null, refresh_token: null, isAuthenticated: false }),

      setTokens: (access_token) => set({ access_token }),
    }),
    {
      name: 'cargozen-auth',
      partialize: (state) => ({
        user: state.user,
        // Only persist refresh_token, not access_token (security)
        refresh_token: state.refresh_token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
