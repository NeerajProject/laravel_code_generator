import { Link, useForm } from "@inertiajs/react";
import { useState } from "react";
import One2ManyField from "@/Components/Generated/One2ManyField";

export default function Form({ record, lookups = {} }) {
    const { data, setData, post, put, processing, errors } = useForm({
        ...record,
        is_active: record?.is_active ?? false,
    });

    const [activeTab, setActiveTab] = useState("");

    const submit = (e) => {
        e.preventDefault();
        record ? put(`/sale-order-lines/${record.id}`) : post("/sale-order-lines");
    };

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
                        <Link href="/sale-order-lines" className="text-sm font-medium text-gray-500 hover:text-[#714B67] transition">ResPartner</Link>
                        <span className="text-gray-300">/</span>
                        <span className="text-sm font-bold text-gray-900">{record ? (data.name || record.name || "Edit") : "New"}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            type="button"
                            onClick={submit}
                            disabled={processing}
                            className="rounded bg-[#714B67] hover:bg-[#5a3b52] px-4 py-1.5 text-sm font-semibold text-white shadow-sm transition disabled:opacity-50 flex items-center gap-1.5 cursor-pointer"
                        >
                            {processing ? "Saving..." : "Save"}
                        </button>
                        <Link
                            href={record ? `/sale-order-lines/${record.id}` : "/sale-order-lines"}
                            className="rounded border border-gray-300 bg-white px-3.5 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-sm transition"
                        >
                            Discard
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
                    <div className="mb-6">
                        <label className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-1">Name</label>
                        <input
                            type="text"
                            value={data.name ?? ""}
                            onChange={(e) => setData("name", e.target.value)}
                            placeholder="e.g. Internal Website Project"
                            className="text-2xl sm:text-3xl font-bold text-gray-900 border-0 border-b-2 border-gray-200 focus:border-[#714B67] focus:ring-0 px-0 py-1 w-full placeholder:text-gray-300 transition"
                            required
                        />
                        {errors.name && <p className="mt-1 text-xs text-red-600">{errors.name}</p>}
                    </div>

                    {/* 2-Column Standard Field Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-4 mb-8">
                        
                <div className="space-y-1">
                    <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600">Email</label>
                    <input
                        type="text"
                        value={data.email ?? ""}
                        onChange={(e) => setData("email", e.target.value)}
                        placeholder="Email..."
                        className="w-full text-sm rounded border-gray-300 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm py-1.5 px-3"
                    />
                    {errors.email && <p className="text-xs text-red-600">{errors.email}</p>}
                </div>
                <div className="space-y-1">
                    <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600">Phone</label>
                    <input
                        type="text"
                        value={data.phone ?? ""}
                        onChange={(e) => setData("phone", e.target.value)}
                        placeholder="Phone..."
                        className="w-full text-sm rounded border-gray-300 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm py-1.5 px-3"
                    />
                    {errors.phone && <p className="text-xs text-red-600">{errors.phone}</p>}
                </div>
                <div className="space-y-1">
                    <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600">Address</label>
                    <input
                        type="text"
                        value={data.address ?? ""}
                        onChange={(e) => setData("address", e.target.value)}
                        placeholder="Address..."
                        className="w-full text-sm rounded border-gray-300 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm py-1.5 px-3"
                    />
                    {errors.address && <p className="text-xs text-red-600">{errors.address}</p>}
                </div>
                <div className="flex items-center gap-3 pt-5">
                    <input
                        type="checkbox"
                        id="is_active"
                        checked={Boolean(data.is_active)}
                        onChange={(e) => setData("is_active", e.target.checked)}
                        className="rounded border-gray-300 text-[#714B67] focus:ring-[#714B67] w-4 h-4 cursor-pointer"
                    />
                    <label htmlFor="is_active" className="text-sm font-semibold text-gray-700 cursor-pointer select-none">
                        Is Active
                    </label>
                    {errors.is_active && <p className="text-xs text-red-600">{errors.is_active}</p>}
                </div>
                    </div>
                    
                </div>
            </div>
        </div>
    );
}
