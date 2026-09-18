import { Link, router } from "@inertiajs/react";
import { useState } from "react";

export default function Show({ record }) {
    const [activeTab, setActiveTab] = useState("");

    return (
        <div className="min-h-screen bg-[#f8fafc]">
            {/* Odoo Top Navigation Bar */}
            <nav className="bg-[#714B67] text-white px-6 py-2.5 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
                        <span className="text-xl">⠿</span>
                        <span>credit:float</span>
                    </div>
                    <div className="flex items-center gap-4 text-sm font-medium text-purple-100">
                        <Link href="/journal-entry-lines" className="hover:text-white transition">credit:float</Link>
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
                        <Link href="/journal-entry-lines" className="text-sm font-medium text-gray-500 hover:text-[#714B67] transition">ResPartner</Link>
                        <span className="text-gray-300">/</span>
                        <span className="text-sm font-bold text-gray-900">{record.name || "Untitled"}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Link
                            href={`/journal-entry-lines/${record.id}/edit`}
                            className="inline-flex items-center gap-1.5 rounded bg-[#714B67] hover:bg-[#5a3b52] px-4 py-1.5 text-sm font-semibold text-white shadow-sm transition"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                            </svg>
                            Edit
                        </Link>
                        <Link
                            href="/journal-entry-lines/create"
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
                        
                    </div>

                    {/* Title Area */}
                    <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight mb-6">
                        {record.name || "Untitled"}
                    </h1>

                    {/* 2-Column Fields Grid */}
                    <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-2 mb-8">
                        
                <div className="border-b border-gray-100 py-2.5">
                    <dt className="text-xs font-semibold uppercase tracking-wider text-gray-500">Email</dt>
                    <dd className="mt-1 text-sm font-medium text-gray-900">{record.email ?? "-"}</dd>
                </div>
                <div className="border-b border-gray-100 py-2.5">
                    <dt className="text-xs font-semibold uppercase tracking-wider text-gray-500">Phone</dt>
                    <dd className="mt-1 text-sm font-medium text-gray-900">{record.phone ?? "-"}</dd>
                </div>
                <div className="border-b border-gray-100 py-2.5">
                    <dt className="text-xs font-semibold uppercase tracking-wider text-gray-500">Address</dt>
                    <dd className="mt-1 text-sm font-medium text-gray-900">{record.address ?? "-"}</dd>
                </div>
                <div className="border-b border-gray-100 py-2.5">
                    <dt className="text-xs font-semibold uppercase tracking-wider text-gray-500">Is Active</dt>
                    <dd className="mt-1 text-sm font-medium text-gray-900">{record.is_active ? <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800">Active</span> : <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">Inactive</span>}</dd>
                </div>
                    </dl>
                    
                </div>
            </div>
        </div>
    );
}
