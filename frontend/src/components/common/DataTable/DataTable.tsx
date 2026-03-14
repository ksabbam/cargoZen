import { useState, useMemo } from 'react'
import {
  ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Search, Download, RefreshCw, SlidersHorizontal
} from 'lucide-react'
import clsx from 'clsx'

export interface Column<T = Record<string, unknown>> {
  key: string
  label: string
  visible?: boolean
  sortable?: boolean
  width?: string
  align?: 'left' | 'right' | 'center'
  render?: (value: unknown, row: T) => React.ReactNode
}

interface DataTableProps<T = Record<string, unknown>> {
  columns: Column<T>[]
  data: T[]
  total?: number
  page?: number
  limit?: number
  onPageChange?: (page: number) => void
  onSearch?: (q: string) => void
  onExport?: () => void
  onRefresh?: () => void
  onFilter?: () => void
  isLoading?: boolean
  rowActions?: (row: T) => React.ReactNode
  getRowKey?: (row: T) => string | number
  searchPlaceholder?: string
  emptyMessage?: string
}

export default function DataTable<T = Record<string, unknown>>({
  columns, data, total = 0, page = 1, limit = 20,
  onPageChange, onSearch, onExport, onRefresh, onFilter,
  isLoading, rowActions, getRowKey, searchPlaceholder = 'Search…', emptyMessage = 'No records found',
}: DataTableProps<T>) {
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  const visibleCols = useMemo(() => columns.filter(c => c.visible !== false), [columns])
  const totalPages = Math.max(1, Math.ceil(total / limit))

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value)
    onSearch?.(e.target.value)
  }

  const handleSort = (key: string) => {
    setSortKey(prev => (prev === key ? key : key))
    setSortDir(prev => (sortKey === key ? (prev === 'asc' ? 'desc' : 'asc') : 'asc'))
  }

  const getCellValue = (row: T, key: string) => (row as Record<string, unknown>)[key]
  const getKey = (row: T, idx: number) => getRowKey ? getRowKey(row) : ((row as Record<string, unknown>).id as string) || idx

  // Page numbers to render
  const pages = useMemo(() => {
    const arr: number[] = []
    const start = Math.max(1, page - 2)
    const end = Math.min(totalPages, start + 4)
    for (let p = start; p <= end; p++) arr.push(p)
    return arr
  }, [page, totalPages])

  return (
    <div className="card flex flex-col overflow-hidden" style={{ height: 'calc(100vh - 180px)' }}>
      {/* Toolbar */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-ios-gray5 shrink-0">
        {onSearch && (
          <div className="relative flex-1 max-w-xs">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ios-gray2 pointer-events-none" />
            <input
              value={search}
              onChange={handleSearch}
              placeholder={searchPlaceholder}
              className="input pl-9 py-2 text-sm"
            />
          </div>
        )}
        <div className="flex items-center gap-1.5 ml-auto">
          {onFilter && (
            <button onClick={onFilter} className="btn-secondary btn-sm gap-1.5">
              <SlidersHorizontal size={13} /> Filter
            </button>
          )}
          {onExport && (
            <button onClick={onExport} className="btn-secondary btn-sm" title="Export">
              <Download size={14} />
            </button>
          )}
          {onRefresh && (
            <button onClick={onRefresh} className="btn-secondary btn-sm" title="Refresh">
              <RefreshCw size={14} className={isLoading ? 'spin' : ''} />
            </button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full min-w-max">
          <thead className="sticky top-0 z-10 bg-[#F9F9F9] border-b border-ios-gray5">
            <tr>
              {visibleCols.map(col => (
                <th
                  key={col.key}
                  className={clsx('th', col.sortable && 'cursor-pointer hover:bg-ios-gray6 select-none')}
                  style={col.width ? { width: col.width } : undefined}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className={clsx('flex items-center gap-1', col.align === 'right' && 'justify-end', col.align === 'center' && 'justify-center')}>
                    {col.label}
                    {col.sortable && sortKey === col.key && (
                      sortDir === 'asc' ? <ChevronUp size={11} className="text-ios-blue" /> : <ChevronDown size={11} className="text-ios-blue" />
                    )}
                  </div>
                </th>
              ))}
              {rowActions && <th className="th w-24 text-right">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-ios-gray5">
            {isLoading ? (
              Array(8).fill(0).map((_, i) => (
                <tr key={i}>
                  {visibleCols.map(c => (
                    <td key={c.key} className="td">
                      <div className="h-4 bg-ios-gray6 rounded animate-pulse" style={{ width: `${60 + Math.random() * 40}%` }} />
                    </td>
                  ))}
                  {rowActions && <td className="td" />}
                </tr>
              ))
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={visibleCols.length + (rowActions ? 1 : 0)} className="py-16">
                  <div className="flex flex-col items-center text-ios-gray2">
                    <div className="w-12 h-12 rounded-full bg-ios-gray6 flex items-center justify-center mb-3">
                      <Search size={20} className="opacity-40" />
                    </div>
                    <p className="text-sm font-medium">{emptyMessage}</p>
                    <p className="text-xs mt-1">Try adjusting your filters</p>
                  </div>
                </td>
              </tr>
            ) : (
              data.map((row, idx) => (
                <tr key={getKey(row, idx)} className="group hover:bg-[#F5F8FF] transition-colors duration-100">
                  {visibleCols.map(col => (
                    <td key={col.key} className={clsx('td', col.align === 'right' && 'text-right', col.align === 'center' && 'text-center')}>
                      {col.render
                        ? col.render(getCellValue(row, col.key), row)
                        : (() => { const v = getCellValue(row, col.key); return v == null ? <span className="text-ios-gray3">—</span> : String(v) })()
                      }
                    </td>
                  ))}
                  {rowActions && (
                    <td className="td text-right">
                      <div className="flex items-center justify-end gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                        {rowActions(row)}
                      </div>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {total > 0 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-ios-gray5 bg-[#FAFAFA] shrink-0">
          <p className="text-xs text-ios-gray">
            <span className="font-medium text-[#1C1C1E]">{(page - 1) * limit + 1}–{Math.min(page * limit, total)}</span>
            {' '}of{' '}
            <span className="font-medium text-[#1C1C1E]">{total.toLocaleString()}</span> records
          </p>
          <div className="flex items-center gap-1">
            <button
              onClick={() => onPageChange?.(page - 1)} disabled={page <= 1}
              className="w-7 h-7 rounded-lg flex items-center justify-center text-ios-gray hover:bg-ios-gray6 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            >
              <ChevronLeft size={14} />
            </button>
            {pages.map(p => (
              <button key={p} onClick={() => onPageChange?.(p)}
                      className={clsx(
                        'w-7 h-7 rounded-lg text-xs font-medium transition-all',
                        p === page ? 'bg-ios-blue text-white shadow-sm' : 'text-ios-gray hover:bg-ios-gray6'
                      )}>
                {p}
              </button>
            ))}
            <button
              onClick={() => onPageChange?.(page + 1)} disabled={page >= totalPages}
              className="w-7 h-7 rounded-lg flex items-center justify-center text-ios-gray hover:bg-ios-gray6 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}