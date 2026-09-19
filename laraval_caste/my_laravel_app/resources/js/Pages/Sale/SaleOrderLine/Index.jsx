import React, { useState } from 'react';
import { Head, Link, router } from '@inertiajs/react';

export default function Index({ records, filters = {} }) {
    const [search, setSearch] = useState(filters.search || '');

    const submitSearch = (e) => {
        e.preventDefault();
        router.get('/sale-order-lines', { search }, { preserveState: true, replace: true });
    };

    const remove = (id) => {
        if (!confirm('Delete this record?')) return;
        router.delete(`/sale-order-lines/${id}`);
    };

    return (
        <div className="min-h-screen bg-slate-50">
            <Head title="Sale Order Line" />

            {/* Page Header */}
            <div className="bg-white border-b border-slate-200">
                <div className="max-w-7xl mx-auto px-6 py-5">
                    <div className="flex items-center justify-between flex-wrap gap-3">
                        <div>
                            <nav className="text-xs text-slate-500 mb-1">
                                <span>Home</span>
                                <span className="mx-1.5">/</span>
                                <span className="text-slate-700 font-medium">Sale Order Line</span>
                            </nav>
                            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Sale Order Line</h1>
                        </div>
                        <div className="flex items-center gap-2">
                            <button type="button" className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" /></svg>
                                Filter
                            </button>
                            <button type="button" className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                                Export
                            </button>
                            <Link href="/sale-order-lines/create" className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40 transition">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                                New Record
                            </Link>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-6">
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">

                    {/* Toolbar */}
                    <div className="px-5 py-3 border-b border-slate-200 flex items-center justify-between gap-3 flex-wrap">
                        <form onSubmit={submitSearch} className="relative flex-1 max-w-md">
                            <svg className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                <circle cx="11" cy="11" r="7" />
                                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35" />
                            </svg>
                            <input
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                placeholder="Search records..."
                                className="w-full pl-9 pr-3 py-2 text-sm bg-white border border-slate-300 rounded-md placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 transition"
                            />
                        </form>
                        <div className="text-xs text-slate-500">
                            {records.total !== undefined ? `${records.total} record${records.total !== 1 ? 's' : ''}` : ''}
                        </div>
                    </div>

                    {/* Table */}
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="bg-slate-50 border-b border-slate-200">
                                    <th className="w-10 px-4 py-3">
                                        <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
                                    </th>
                                    <th className="px-5 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Product Id</th>
                                    <th className="px-5 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Quantity</th>
                                    <th className="px-5 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Unit Price</th>
                                    <th className="px-5 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Subtotal</th>
                                    <th className="px-5 py-3 text-right text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {records.data.length === 0 && (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-16 text-center">
                                            <div className="flex flex-col items-center gap-2 text-slate-400">
                                                <svg className="w-12 h-12" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                </svg>
                                                <p className="text-sm font-medium">No records found</p>
                                                <p className="text-xs">Try adjusting your search or create a new record.</p>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                                {records.data.map((row) => (
                                    <tr key={row.id} className="hover:bg-slate-50/70 transition-colors">
                                        <td className="px-4 py-3">
                                            <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
                                        </td>
                                        <td className="px-5 py-3 text-slate-700 whitespace-nowrap">
                                            {row.product?.name || row.product_id || '-'}
                                        </td>
                                        <td className="px-5 py-3 text-slate-700 whitespace-nowrap">
                                            <span className="font-medium text-slate-900 tabular-nums">{Number(row.quantity ?? 0).toFixed(2)}</span>
                                        </td>
                                        <td className="px-5 py-3 text-slate-700 whitespace-nowrap">
                                            <span className="font-medium text-slate-900 tabular-nums">{Number(row.unit_price ?? 0).toFixed(2)}</span>
                                        </td>
                                        <td className="px-5 py-3 text-slate-700 whitespace-nowrap">
                                            <span className="font-medium text-slate-900 tabular-nums">{Number(row.subtotal ?? 0).toFixed(2)}</span>
                                        </td>
                                        <td className="px-5 py-3 text-right whitespace-nowrap">
                                            <div className="inline-flex items-center gap-1">
                                                <Link href={`/sale-order-lines/${row.id}/edit`} className="inline-flex items-center justify-center w-8 h-8 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-md transition" title="Edit">
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                                                </Link>
                                                <button onClick={() => remove(row.id)} className="inline-flex items-center justify-center w-8 h-8 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-md transition" title="Delete">
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M9 7V4a1 1 0 011-1h4a1 1 0 011 1v3" /></svg>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    {records.links && records.links.length > 3 && (
                        <div className="px-5 py-3 border-t border-slate-200 flex items-center justify-between gap-3 flex-wrap bg-slate-50/40">
                            <div className="text-xs text-slate-500">
                                Showing <span className="font-medium text-slate-700">{records.from ?? 0}</span> to <span className="font-medium text-slate-700">{records.to ?? 0}</span> of <span className="font-medium text-slate-700">{records.total}</span> entries
                            </div>
                            <div className="flex items-center gap-1">
                                {records.links.map((link, i) => (
                                    <button
                                        key={i}
                                        disabled={!link.url}
                                        onClick={() => link.url && router.get(link.url, {}, { preserveState: true })}
                                        dangerouslySetInnerHTML={{ __html: link.label }}
                                        className={`min-w-[32px] h-8 px-2 text-xs font-medium rounded-md border transition ${link.active ? 'bg-blue-600 text-white border-blue-600 shadow-sm' : 'bg-white text-slate-600 border-slate-300 hover:bg-slate-100'} ${!link.url ? 'opacity-40 cursor-not-allowed' : ''}`}
                                    />
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
