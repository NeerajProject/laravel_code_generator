import { Link, router } from "@inertiajs/react";
import { useState } from "react";

export default function Show({ record }) {
    const [activeTab, setActiveTab] = useState("order_line_ids");

    return (
        <div className="min-h-screen bg-[#f8fafc]">
            {/* Odoo Top Navigation Bar */}
            <nav className="bg-[#714B67] text-white px-6 py-2.5 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
                        <span className="text-xl">⠿</span>
                        <span>subtotal:float=compute_subtotal</span>
                    </div>
                    <div className="flex items-center gap-4 text-sm font-medium text-purple-100">
                        <Link href="/sale-order-lines" className="hover:text-white transition">subtotal:float=compute_subtotal</Link>
                    </div>
                </div>
                <div className="flex items-center gap-3 text-xs text-purple-200">
                    <span className="w-7 h-7 rounded-full bg-purple-900/60 border border-purple-400/40 flex items-center justify-center font-bold text-white text-xs">
                        NJ
                    </span>
                </div>
            </nav>

            {/* Odoo Control Panel */}
            <div className="bg-white border-b border-gray-200 px-6 py-3 shadow-2xs">
                <div className="max-w-5xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Link href="/sale-order-lines" className="text-sm font-medium text-gray-500 hover:text-[#714B67] transition">SaleOrder</Link>
                        <span className="text-gray-300">/</span>
                        <span className="text-sm font-bold text-gray-900">{record.name || "Untitled"}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Link
                            href={`/sale-order-lines/${record.id}/edit`}
                            className="inline-flex items-center gap-1.5 rounded bg-[#714B67] hover:bg-[#5a3b52] px-4 py-1.5 text-sm font-semibold text-white shadow-sm transition"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                            </svg>
                            Edit
                        </Link>
                        <Link
                            href="/sale-order-lines/create"
                            className="rounded border border-gray-300 bg-white px-3.5 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-sm transition"
                        >
                            New
                        </Link>
                        
                    </div>
                </div>
            </div>

            {/* Form Sheet Canvas */}
            <div className="py-6 px-4">
                <div className="max-w-5xl mx-auto bg-white border border-gray-200/90 shadow-2xs rounded-sm p-6 sm:p-10 mb-10">
                    {/* Smart Buttons Box */}
                    <div className="flex justify-end mb-6 -mt-2 -mr-2 gap-2">
                        
                    <div className="flex flex-col items-center justify-center border border-gray-200 rounded px-4 py-1.5 bg-gray-50/70 text-right shadow-2xs">
                        <span className="text-xl font-bold text-gray-900 leading-tight">
                            {record.order_line_ids?.length || 0}
                        </span>
                        <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
                            Order Line
                        </span>
                    </div>
                    </div>

                    {/* Title Area */}
                    <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight mb-6">
                        {record.name || "Untitled"}
                    </h1>

                    {/* 2-Column Fields Grid */}
                    <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-2 mb-8">
                        
                <div className="border-b border-gray-100 py-2.5">
                    <dt className="text-xs font-semibold uppercase tracking-wider text-gray-500">Customer</dt>
                    <dd className="mt-1 text-sm font-medium text-gray-900">{record.customer_id?.name ?? record.customer_id ?? "-"}</dd>
                </div>
                <div className="border-b border-gray-100 py-2.5">
                    <dt className="text-xs font-semibold uppercase tracking-wider text-gray-500">Order Date</dt>
                    <dd className="mt-1 text-sm font-medium text-gray-900">{record.order_date ?? "-"}</dd>
                </div>
                <div className="border-b border-gray-100 py-2.5">
                    <dt className="text-xs font-semibold uppercase tracking-wider text-gray-500">State</dt>
                    <dd className="mt-1 text-sm font-medium text-gray-900">{record.state ?? "-"}</dd>
                </div>
                <div className="border-b border-gray-100 py-2.5">
                    <dt className="text-xs font-semibold uppercase tracking-wider text-gray-500">Note</dt>
                    <dd className="mt-1 text-sm font-medium text-gray-900">{record.note ?? "-"}</dd>
                </div>
                    </dl>
                    
                {/* Notebook / Tabs */}
                <div className="mt-8 border-t border-gray-100 pt-6">
                    <div className="flex border-b border-gray-200 space-x-6">
                        
                        <button
                            type="button"
                            onClick={() => setActiveTab("order_line_ids")}
                            className={`pb-2.5 px-3 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
                                activeTab === "order_line_ids"
                                    ? "border-[#714B67] text-[#714B67]"
                                    : "border-transparent text-gray-500 hover:text-gray-700"
                            }`}
                        >
                            <span>Order Line</span>
                            <span className="px-1.5 py-0.5 rounded-full text-xs font-bold bg-purple-100 text-[#714B67]">
                                {record.order_line_ids?.length || 0}
                            </span>
                        </button>
                    </div>
                    <div className="pt-4">
                        
                    {activeTab === "order_line_ids" && (
                        <div className="border border-gray-200 rounded overflow-hidden shadow-2xs bg-white mt-2">
                            <table className="min-w-full divide-y divide-gray-200 text-sm">
                                <thead className="bg-gray-50/80">
                                    <tr>
                                        <th className="w-12 px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">#</th>
                                        <th className="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Description</th>
                                        <th className="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Quantity</th>
                                        <th className="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Unit Price</th>
                                        <th className="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Subtotal</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100 bg-white">
                                    {(record.order_line_ids || []).length > 0 ? (
                                        record.order_line_ids.map((line, idx) => (
                                            <tr key={line.id ?? idx} className="hover:bg-gray-50/50">
                                                <td className="px-3 py-2 text-xs font-mono text-gray-400">{idx + 1}</td>
                                        <td className="px-3 py-2 text-sm text-gray-700">{line.name ?? "-"}</td>
                                        <td className="px-3 py-2 text-sm text-gray-700">{line.quantity ?? "-"}</td>
                                        <td className="px-3 py-2 text-sm text-gray-700">{line.price_unit ?? "-"}</td>
                                        <td className="px-3 py-2 text-sm text-gray-700">{line.subtotal ?? "-"}</td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan={5} className="px-4 py-8 text-center text-sm text-gray-500">
                                                No order line recorded for this saleorder.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                    </div>
                </div>
                </div>
            </div>
        </div>
    );
}
