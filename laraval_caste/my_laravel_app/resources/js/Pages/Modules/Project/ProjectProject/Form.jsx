import { Link, useForm } from "@inertiajs/react";
import { useState } from "react";
import One2ManyField from "@/Components/Generated/One2ManyField";

export default function Form({ record, lookups = {} }) {
    const { data, setData, post, put, processing, errors } = useForm({
        ...record,
        is_active: record?.is_active ?? false,
        task_ids: record?.task_ids ?? [],
    });

    const [activeTab, setActiveTab] = useState("task_ids");

    const submit = (e) => {
        e.preventDefault();
        record ? put(`/tasks/${record.id}`) : post("/tasks");
    };

    return (
        <div className="min-h-screen bg-[#f8fafc]">
            {/* Odoo Top Navigation Bar */}
            <nav className="bg-[#714B67] text-white px-6 py-2.5 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
                        <span className="text-xl">⠿</span>
                        <span>Project</span>
                    </div>
                    <div className="flex items-center gap-4 text-sm font-medium text-purple-100">
                        <Link href="/tasks" className="hover:text-white transition">Task Masters</Link>
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
                        <Link href="/tasks" className="text-sm font-medium text-gray-500 hover:text-[#714B67] transition">ProjectProject</Link>
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
                            href={record ? `/tasks/${record.id}` : "/tasks"}
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
                        onClick={() => setActiveTab("task_ids")}
                        className="flex flex-col items-center justify-center border border-gray-200 rounded px-4 py-1.5 bg-gray-50/70 hover:bg-purple-50 hover:border-purple-200 transition text-right shadow-2xs cursor-pointer"
                    >
                        <span className="text-xl font-bold text-gray-900 leading-tight">
                            {data.task_ids?.length || 0}
                        </span>
                        <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
                            Task
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
                    <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600">Code</label>
                    <input
                        type="text"
                        value={data.code ?? ""}
                        onChange={(e) => setData("code", e.target.value)}
                        placeholder="Code..."
                        className="w-full text-sm rounded border-gray-300 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm py-1.5 px-3"
                    />
                    {errors.code && <p className="text-xs text-red-600">{errors.code}</p>}
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
                    
                {/* Notebook / Tabs */}
                <div className="mt-8 border-t border-gray-100 pt-6">
                    <div className="flex border-b border-gray-200 space-x-6">
                        
                        <button
                            type="button"
                            onClick={() => setActiveTab("task_ids")}
                            className={`pb-2.5 px-3 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
                                activeTab === "task_ids"
                                    ? "border-[#714B67] text-[#714B67]"
                                    : "border-transparent text-gray-500 hover:text-gray-700"
                            }`}
                        >
                            <span>Task</span>
                            <span className="px-1.5 py-0.5 rounded-full text-xs font-bold bg-purple-100 text-[#714B67]">
                                {data.task_ids?.length || 0}
                            </span>
                        </button>
                        <button
                            type="button"
                            onClick={() => setActiveTab("description")}
                            className={`pb-2.5 px-3 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
                                activeTab === "description"
                                    ? "border-[#714B67] text-[#714B67]"
                                    : "border-transparent text-gray-500 hover:text-gray-700"
                            }`}
                        >
                            Description
                        </button>
                    </div>
                    <div className="pt-4">
                        
                    {activeTab === "task_ids" && (
                        <One2ManyField
                            name="task_ids"
                            label="Task"
                            value={data.task_ids || []}
                            onChange={(lines) => setData("task_ids", lines)}
                            columns={[{"name": "name", "label": "Task Title", "type": "text", "placeholder": "e.g. Design homepage"}, {"name": "description", "label": "Description", "type": "text", "placeholder": "Details..."}, {"name": "is_done", "label": "Done", "type": "bool"}]}
                            error={errors.task_ids}
                        />
                    )}
                    {activeTab === "description" && (
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">Description / Notes</label>
                            <textarea
                                value={data.description ?? ""}
                                onChange={(e) => setData("description", e.target.value)}
                                rows={6}
                                className="w-full rounded border-gray-300 text-sm focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm p-3"
                                placeholder="Add detailed notes or description..."
                            />
                            {errors.description && <p className="text-xs text-red-600 mt-1">{errors.description}</p>}
                        </div>
                    )}
                    </div>
                </div>
                </div>
            </div>
        </div>
    );
}
