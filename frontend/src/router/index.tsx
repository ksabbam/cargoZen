import { lazy, Suspense } from 'react'
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import ProtectedRoute from './ProtectedRoute'
import AppLayout from '@/components/layout/AppLayout'

// Lazy load all pages
const LoginPage = lazy(() => import('@/pages/auth/LoginPage'))
const DashboardPage = lazy(() => import('@/pages/dashboard/DashboardPage'))

// Administration pages
const OrganizationsPage = lazy(() => import('@/pages/administration/organizations/OrganizationsPage'))
const OrgGroupsPage = lazy(() => import('@/pages/administration/org-groups/OrgGroupsPage'))
const AirlinesPage = lazy(() => import('@/pages/administration/airlines/AirlinesPage'))
const ShippingLinesPage = lazy(() => import('@/pages/administration/shipping-lines/ShippingLinesPage'))
const AccountsPage = lazy(() => import('@/pages/administration/accounts/AccountsPage'))
const ChargeMasterPage = lazy(() => import('@/pages/administration/charge-master/ChargeMasterPage'))
const DefaultChargesPage = lazy(() => import('@/pages/administration/default-charges/DefaultChargesPage'))
const CommoditiesPage = lazy(() => import('@/pages/administration/commodities/CommoditiesPage'))
const BusinessDimensionsPage = lazy(() => import('@/pages/administration/business-dimensions/BusinessDimensionsPage'))
const VendorContractsPage = lazy(() => import('@/pages/administration/vendor-contracts/VendorContractsPage'))
const CustomClearingPage = lazy(() => import('@/pages/administration/custom-clearing/CustomClearingPage'))
const SystemSettingsPage = lazy(() => import('@/pages/administration/system-settings/SystemSettingsPage'))

// Transaction pages
const ImportJobsPage = lazy(() => import('@/pages/transactions/import-jobs/ImportJobsPage'))
const BankPaymentsPage = lazy(() => import('@/pages/transactions/bank-payments/BankPaymentsPage'))
const BankReceiptsPage = lazy(() => import('@/pages/transactions/bank-receipts/BankReceiptsPage'))
const JournalEntriesPage = lazy(() => import('@/pages/transactions/journal-entries/JournalEntriesPage'))
const PurchaseBillsPage = lazy(() => import('@/pages/transactions/purchase-bills/PurchaseBillsPage'))
const DebitNotesPage = lazy(() => import('@/pages/transactions/debit-notes/DebitNotesPage'))
const CustomsExportPage = lazy(() => import('@/pages/transactions/customs-export/CustomsExportPage'))

// Other pages
const ReportsPage = lazy(() => import('@/pages/reports/ReportsPage'))
const ToolsPage = lazy(() => import('@/pages/tools/ToolsPage'))

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="flex items-center gap-3 text-gray-400">
        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span>Loading...</span>
      </div>
    </div>
  )
}

const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <Suspense fallback={<LoadingFallback />}>
        <LoginPage />
      </Suspense>
    ),
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <Suspense fallback={<LoadingFallback />}><DashboardPage /></Suspense> },
          { path: '/administration/organizations', element: <Suspense fallback={<LoadingFallback />}><OrganizationsPage /></Suspense> },
          { path: '/administration/org-groups', element: <Suspense fallback={<LoadingFallback />}><OrgGroupsPage /></Suspense> },
          { path: '/administration/airlines', element: <Suspense fallback={<LoadingFallback />}><AirlinesPage /></Suspense> },
          { path: '/administration/shipping-lines', element: <Suspense fallback={<LoadingFallback />}><ShippingLinesPage /></Suspense> },
          { path: '/administration/accounts', element: <Suspense fallback={<LoadingFallback />}><AccountsPage /></Suspense> },
          { path: '/administration/charge-master', element: <Suspense fallback={<LoadingFallback />}><ChargeMasterPage /></Suspense> },
          { path: '/administration/default-charges', element: <Suspense fallback={<LoadingFallback />}><DefaultChargesPage /></Suspense> },
          { path: '/administration/business-dimensions', element: <Suspense fallback={<LoadingFallback />}><BusinessDimensionsPage /></Suspense> },
          { path: '/administration/commodities', element: <Suspense fallback={<LoadingFallback />}><CommoditiesPage /></Suspense> },
          { path: '/administration/vendor-contracts', element: <Suspense fallback={<LoadingFallback />}><VendorContractsPage /></Suspense> },
          { path: '/administration/custom-clearing', element: <Suspense fallback={<LoadingFallback />}><CustomClearingPage /></Suspense> },
          { path: '/administration/system-settings', element: <Suspense fallback={<LoadingFallback />}><SystemSettingsPage /></Suspense> },
          { path: '/transactions/import-jobs', element: <Suspense fallback={<LoadingFallback />}><ImportJobsPage /></Suspense> },
          { path: '/transactions/bank-payments', element: <Suspense fallback={<LoadingFallback />}><BankPaymentsPage /></Suspense> },
          { path: '/transactions/bank-receipts', element: <Suspense fallback={<LoadingFallback />}><BankReceiptsPage /></Suspense> },
          { path: '/transactions/journal-entries', element: <Suspense fallback={<LoadingFallback />}><JournalEntriesPage /></Suspense> },
          { path: '/transactions/debit-notes', element: <Suspense fallback={<LoadingFallback />}><DebitNotesPage /></Suspense> },
          { path: '/transactions/purchase-bills', element: <Suspense fallback={<LoadingFallback />}><PurchaseBillsPage /></Suspense> },
          { path: '/transactions/customs-export', element: <Suspense fallback={<LoadingFallback />}><CustomsExportPage /></Suspense> },
          { path: '/reports', element: <Suspense fallback={<LoadingFallback />}><ReportsPage /></Suspense> },
          { path: '/tools', element: <Suspense fallback={<LoadingFallback />}><ToolsPage /></Suspense> },
          { path: '*', element: <Navigate to="/" replace /> },
        ],
      },
    ],
  },
])

export default function AppRouter() {
  return <RouterProvider router={router} />
}
