/// <reference types="vite/client" />

interface ImportMeta {
  readonly env: ImportMetaEnv
}

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  [key: string]: string | boolean | undefined
}

// lucide-react type stub (in case package types are not available)
declare module 'lucide-react' {
  import { FC, SVGProps } from 'react'
  export interface LucideProps extends SVGProps<SVGSVGElement> {
    size?: number | string
    absoluteStrokeWidth?: boolean
  }
  export type LucideIcon = FC<LucideProps>
  export const LayoutDashboard: LucideIcon
  export const Building2: LucideIcon
  export const Plane: LucideIcon
  export const Ship: LucideIcon
  export const DollarSign: LucideIcon
  export const Package: LucideIcon
  export const FileText: LucideIcon
  export const Settings: LucideIcon
  export const ChevronDown: LucideIcon
  export const ChevronRight: LucideIcon
  export const ChevronLeft: LucideIcon
  export const ChevronUp: LucideIcon
  export const LogOut: LucideIcon
  export const Menu: LucideIcon
  export const X: LucideIcon
  export const Briefcase: LucideIcon
  export const TrendingUp: LucideIcon
  export const Receipt: LucideIcon
  export const BookOpen: LucideIcon
  export const CreditCard: LucideIcon
  export const FileBarChart: LucideIcon
  export const Wrench: LucideIcon
  export const Users: LucideIcon
  export const Layers: LucideIcon
  export const Tag: LucideIcon
  export const Star: LucideIcon
  export const Anchor: LucideIcon
  export const Plus: LucideIcon
  export const Edit2: LucideIcon
  export const Trash2: LucideIcon
  export const Eye: LucideIcon
  export const EyeOff: LucideIcon
  export const LogIn: LucideIcon
  export const Search: LucideIcon
  export const Download: LucideIcon
  export const RefreshCw: LucideIcon
  export const Settings2: LucideIcon
  export const Filter: LucideIcon
  export const ArrowLeft: LucideIcon
  export const BarChart3: LucideIcon
  export const AlertCircle: LucideIcon
  export const CheckCircle: LucideIcon
  export const XCircle: LucideIcon
  export const Clock: LucideIcon
  export const Bell: LucideIcon
  export const ArrowRight: LucideIcon
  export const SlidersHorizontal: LucideIcon
  export const ChevronLeft: LucideIcon
}
