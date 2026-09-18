import { Link, useForm } from "@inertiajs/react";
import { useState } from "react";
import One2ManyField from "@/Components/Generated/One2ManyField";

export default function Form({ record, lookups = {} }) {
    const { data, setData, post, put, processing, errors } = useForm({
        ...record,
        order_line_ids: record?.order_line_ids ?? [],
    });

    const [activeTab, setActiveTab] = useState("order_line_ids");

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
                        <Link href="/sale-order-lines" className="text-sm font-medium text-gray-500 hover:text-[#714B67] transition">SaleOrder</Link>
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
                        
                    <button
                        type="button"
                        onClick={() => setActiveTab("order_line_ids")}
                        className="flex flex-col items-center justify-center border border-gray-200 rounded px-4 py-1.5 bg-gray-50/70 hover:bg-purple-50 hover:border-purple-200 transition text-right shadow-2xs cursor-pointer"
                    >
                        <span className="text-xl font-bold text-gray-900 leading-tight">
                            {data.order_line_ids?.length || 0}
                        </span>
                        <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
                            Order Line
                        </span>
                    </button>
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
                    <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600">Customer</label>
                    <select
                        value={data.customer_id ?? ""}
                        onChange={(e) => setData("customer_id", e.target.value)}
                        className="w-full text-sm rounded border-gray-300 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm py-1.5 px-3"
                    >
                        <option value="">Select ResPartner</option>
                        {(lookups.customer_id ?? []).map((opt) => (
                            <option key={opt.id} value={opt.id}>{opt.name ?? opt.label ?? opt.id}</option>
                        ))}
                    </select>
                    {errors.customer_id && <p className="text-xs text-red-600">{errors.customer_id}</p>}
                </div>
                <div className="space-y-1">
                    <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600">Order Date</label>
                    <input
                        type="date"
                        value={data.order_date ?? ""}
                        onChange={(e) => setData("order_date", e.target.value)}
                        placeholder="Order Date..."
                        className="w-full text-sm rounded border-gray-300 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm py-1.5 px-3"
                    />
                    {errors.order_date && <p className="text-xs text-red-600">{errors.order_date}</p>}
                </div>
                <div className="space-y-1">
                    <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600">State</label>
                    <input
                        type="text"
                        value={data.state ?? ""}
                        onChange={(e) => setData("state", e.target.value)}
                        placeholder="State..."
                        className="w-full text-sm rounded border-gray-300 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm py-1.5 px-3"
                    />
                    {errors.state && <p className="text-xs text-red-600">{errors.state}</p>}
                </div>
                <div className="space-y-1">
                    <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600">Note</label>
                    <input
                        type="text"
                        value={data.note ?? ""}
                        onChange={(e) => setData("note", e.target.value)}
                        placeholder="Note..."
                        className="w-full text-sm rounded border-gray-300 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm py-1.5 px-3"
                    />
                    {errors.note && <p className="text-xs text-red-600">{errors.note}</p>}
                </div>
                    </div>
                    
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
                                {data.order_line_ids?.length || 0}
                            </span>
                        </button>
                    </div>
                    <div className="pt-4">
                        
                    {activeTab === "order_line_ids" && (
                        <One2ManyField
                            name="order_line_ids"
                            label="Order Line"
                            value={data.order_line_ids || []}
                            onChange={(lines) => setData("order_line_ids", lines)}
                            columns={[{"name": "name", "label": "Description", "type": "text", "placeholder": "Item description"}, {"name": "quantity", "label": "Quantity", "type": "number", "defaultValue": 1}, {"name": "price_unit", "label": "Unit Price", "type": "number", "defaultValue": 0.0}, {"name": "subtotal", "label": "Subtotal", "type": "number", "defaultValue": 0.0}]}
                            error={errors.order_line_ids}
                        />
                    )}
                    </div>
                </div>
                </div>
            </div>
        </div>
    );
}
