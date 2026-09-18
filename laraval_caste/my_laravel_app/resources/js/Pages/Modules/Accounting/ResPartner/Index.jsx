import { Link, router } from "@inertiajs/react";
import { useState } from "react";

export default function Index({ records = [], filters = {} }) {
    const [filtersState, setFiltersState] = useState(filters ?? {});
    const [searchInput, setSearchInput] = useState(filters?.search ?? "");
    const [showFilterMenu, setShowFilterMenu] = useState(false);
    const [selectedIds, setSelectedIds] = useState([]);

    const applyFilters = (newFilters) => {
        const cleaned = {};
        for (const [k, v] of Object.entries(newFilters)) {
            if (v !== undefined && v !== null && v !== "") {
                cleaned[k] = v;
            }
        }
        router.get("/journal-entry-lines", { filters: cleaned }, { preserveState: true, replace: true });
    };

    const handleSearchSubmit = (e) => {
        if (e) e.preventDefault();
        const updated = { ...filtersState, search: searchInput.trim() };
        setFiltersState(updated);
        applyFilters(updated);
    };

    const removeFilter = (key) => {
        const updated = { ...filtersState };
        delete updated[key];
        if (key === "search") setSearchInput("");
        setFiltersState(updated);
        applyFilters(updated);
    };

    const updateSpecificFilter = (key, value) => {
        const updated = { ...filtersState, [key]: value };
        setFiltersState(updated);
        applyFilters(updated);
    };

    const toggleActiveFilter = () => {
        const current = filtersState.is_active;
        const next = current === "true" || current === true ? "" : "true";
        updateSpecificFilter("is_active", next);
    };

    const clearAllFilters = () => {
        setSearchInput("");
        setFiltersState({});
        applyFilters({});
        setShowFilterMenu(false);
    };

    const applySort = (field, direction) => {
        const updated = { ...filtersState, sort_field: field, sort_direction: direction };
        setFiltersState(updated);
        applyFilters(updated);
        setShowFilterMenu(false);
    };

    const toggleSelectAll = () => {
        if (records.length > 0 && selectedIds.length === records.length) {
            setSelectedIds([]);
        } else {
            setSelectedIds(records.map((r) => r.id));
        }
    };

    const toggleSelectRow = (id) => {
        setSelectedIds((prev) =>
            prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
        );
    };

    const activeFilterEntries = Object.entries(filtersState).filter(
        ([k, v]) => k !== "search" && !k.startsWith("sort_") && v !== "" && v !== undefined && v !== null
    );
    const hasActiveFilters = Boolean(searchInput || filtersState.search || activeFilterEntries.length > 0);

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
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    {/* Left: Breadcrumbs & Action Buttons */}
                    <div className="flex items-center gap-4">
                        <h1 className="text-xl font-bold text-gray-900">ResPartner</h1>
                        <Link
                            href="/journal-entry-lines/create"
                            className="inline-flex items-center gap-1.5 rounded bg-[#714B67] hover:bg-[#5a3b52] px-3.5 py-1.5 text-sm font-semibold text-white shadow-sm transition"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                            </svg>
                            New
                        </Link>
                        {selectedIds.length > 0 && (
                            <div className="flex items-center gap-2 pl-3 border-l border-gray-200 text-xs">
                                <span className="font-medium text-gray-600">{selectedIds.length} selected</span>
                            </div>
                        )}
                    </div>

                    {/* Right: Odoo Search Bar, Filters Dropdown, Pager */}
                    <div className="flex items-center gap-3 relative">
                        {/* Search Input Box */}
                        <form
                            onSubmit={handleSearchSubmit}
                            className="relative flex items-center bg-white border border-gray-300 rounded shadow-sm px-2.5 py-1 text-sm min-w-[280px] sm:min-w-[360px] focus-within:ring-2 focus-within:ring-[#714B67] focus-within:border-transparent"
                        >
                            <svg className="w-4 h-4 text-gray-400 mr-1.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>

                            {/* Filter Chips inside search bar */}
                            <div className="flex flex-wrap gap-1 items-center flex-1">
                                {filtersState.search && (
                                    <span className="inline-flex items-center gap-1 bg-purple-100 text-[#714B67] text-xs px-2 py-0.5 rounded font-medium">
                                        Search: &quot;{filtersState.search}&quot;
                                        <button type="button" onClick={() => removeFilter("search")} className="hover:text-purple-900">×</button>
                                    </span>
                                )}
                                {activeFilterEntries.map(([key, val]) => (
                                    <span key={key} className="inline-flex items-center gap-1 bg-purple-50 border border-purple-200 text-[#714B67] text-xs px-2 py-0.5 rounded font-medium">
                                        {key}: {String(val)}
                                        <button type="button" onClick={() => removeFilter(key)} className="hover:text-purple-900">×</button>
                                    </span>
                                ))}
                                <input
                                    type="text"
                                    value={searchInput}
                                    onChange={(e) => setSearchInput(e.target.value)}
                                    placeholder="Search..."
                                    className="border-0 focus:ring-0 text-sm py-0.5 px-1.5 flex-1 min-w-[80px] outline-none text-gray-800 placeholder-gray-400"
                                />
                            </div>

                            {hasActiveFilters && (
                                <button
                                    type="button"
                                    onClick={clearAllFilters}
                                    className="text-gray-400 hover:text-gray-600 p-0.5 mx-1"
                                    title="Clear all filters"
                                >
                                    ×
                                </button>
                            )}

                            {/* Filters Dropdown Trigger Button */}
                            <button
                                type="button"
                                onClick={() => setShowFilterMenu(!showFilterMenu)}
                                className="ml-1 p-1 text-gray-500 hover:text-[#714B67] rounded hover:bg-gray-100 flex items-center gap-1 text-xs font-semibold"
                            >
                                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                                </svg>
                                Filters
                                <span className="text-[10px]">▼</span>
                            </button>
                        </form>

                        {/* Odoo Filter Menu Popover */}
                        {showFilterMenu && (
                            <div className="absolute right-0 top-full mt-2 w-72 bg-white border border-gray-200 rounded-md shadow-xl p-3 z-30 divide-y divide-gray-100 text-xs">
                                <div className="pb-2">
                                    <p className="font-bold text-gray-500 uppercase tracking-wider text-[10px] mb-1.5 flex items-center gap-1">
                                        <span>🔍</span> Quick Filters
                                    </p>
                                    
                        <label className="flex items-center gap-2 py-1.5 text-gray-700 hover:bg-gray-50 px-1 rounded cursor-pointer select-none">
                            <input
                                type="checkbox"
                                checked={filtersState.is_active === "true" || filtersState.is_active === true}
                                onChange={toggleActiveFilter}
                                className="rounded border-gray-300 text-[#714B67] focus:ring-[#714B67]"
                            />
                            <span className="font-medium">Active records only</span>
                        </label>
                                    
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Name</label>
                            <input
                                type="text"
                                value={filtersState.name ?? ""}
                                onChange={(e) => updateSpecificFilter("name", e.target.value)}
                                placeholder="Filter by Name..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Email</label>
                            <input
                                type="text"
                                value={filtersState.email ?? ""}
                                onChange={(e) => updateSpecificFilter("email", e.target.value)}
                                placeholder="Filter by Email..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Phone</label>
                            <input
                                type="text"
                                value={filtersState.phone ?? ""}
                                onChange={(e) => updateSpecificFilter("phone", e.target.value)}
                                placeholder="Filter by Phone..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Code</label>
                            <input
                                type="text"
                                value={filtersState.code ?? ""}
                                onChange={(e) => updateSpecificFilter("code", e.target.value)}
                                placeholder="Filter by Code..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Name</label>
                            <input
                                type="text"
                                value={filtersState.name ?? ""}
                                onChange={(e) => updateSpecificFilter("name", e.target.value)}
                                placeholder="Filter by Name..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Account Type</label>
                            <input
                                type="text"
                                value={filtersState.account_type ?? ""}
                                onChange={(e) => updateSpecificFilter("account_type", e.target.value)}
                                placeholder="Filter by Account Type..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Name</label>
                            <input
                                type="text"
                                value={filtersState.name ?? ""}
                                onChange={(e) => updateSpecificFilter("name", e.target.value)}
                                placeholder="Filter by Name..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Code</label>
                            <input
                                type="text"
                                value={filtersState.code ?? ""}
                                onChange={(e) => updateSpecificFilter("code", e.target.value)}
                                placeholder="Filter by Code..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Journal Type</label>
                            <input
                                type="text"
                                value={filtersState.journal_type ?? ""}
                                onChange={(e) => updateSpecificFilter("journal_type", e.target.value)}
                                placeholder="Filter by Journal Type..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Name</label>
                            <input
                                type="text"
                                value={filtersState.name ?? ""}
                                onChange={(e) => updateSpecificFilter("name", e.target.value)}
                                placeholder="Filter by Name..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Date</label>
                            <input
                                type="text"
                                value={filtersState.date ?? ""}
                                onChange={(e) => updateSpecificFilter("date", e.target.value)}
                                placeholder="Filter by Date..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Journal</label>
                            <input
                                type="text"
                                value={filtersState.journal_id ?? ""}
                                onChange={(e) => updateSpecificFilter("journal_id", e.target.value)}
                                placeholder="Filter by Journal..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Partner</label>
                            <input
                                type="text"
                                value={filtersState.partner_id ?? ""}
                                onChange={(e) => updateSpecificFilter("partner_id", e.target.value)}
                                placeholder="Filter by Partner..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">State</label>
                            <input
                                type="text"
                                value={filtersState.state ?? ""}
                                onChange={(e) => updateSpecificFilter("state", e.target.value)}
                                placeholder="Filter by State..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Account</label>
                            <input
                                type="text"
                                value={filtersState.account_id ?? ""}
                                onChange={(e) => updateSpecificFilter("account_id", e.target.value)}
                                placeholder="Filter by Account..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Partner</label>
                            <input
                                type="text"
                                value={filtersState.partner_id ?? ""}
                                onChange={(e) => updateSpecificFilter("partner_id", e.target.value)}
                                placeholder="Filter by Partner..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">Label</label>
                            <input
                                type="text"
                                value={filtersState.label ?? ""}
                                onChange={(e) => updateSpecificFilter("label", e.target.value)}
                                placeholder="Filter by Label..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>
                                </div>
                                <div className="py-2">
                                    <p className="font-bold text-gray-500 uppercase tracking-wider text-[10px] mb-1.5 flex items-center gap-1">
                                        <span>⇅</span> Sort
                                    </p>
                                    <div className="flex flex-col gap-1">
                                        <button type="button" onClick={() => applySort("name", "asc")} className="text-left px-1.5 py-1 rounded text-gray-700 hover:bg-gray-100 font-medium">Name (A → Z)</button>
                                        <button type="button" onClick={() => applySort("name", "desc")} className="text-left px-1.5 py-1 rounded text-gray-700 hover:bg-gray-100 font-medium">Name (Z → A)</button>
                                        <button type="button" onClick={() => applySort("id", "desc")} className="text-left px-1.5 py-1 rounded text-gray-700 hover:bg-gray-100 font-medium">Newest First</button>
                                    </div>
                                </div>
                                {hasActiveFilters && (
                                    <div className="pt-2">
                                        <button
                                            type="button"
                                            onClick={clearAllFilters}
                                            className="w-full text-left px-1.5 py-1 rounded text-red-600 hover:bg-red-50 font-semibold"
                                        >
                                            Clear All Filters
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Pager */}
                        <div className="text-xs text-gray-500 font-medium whitespace-nowrap hidden sm:block">
                            {records.length > 0 ? `1-${records.length}` : 0} / {records.length}
                        </div>
                    </div>
                </div>
            </div>

            {/* Odoo List Table */}
            <div className="max-w-7xl mx-auto px-6 py-6">
                <div className="bg-white border border-gray-200 rounded shadow-2xs overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200 text-sm">
                        <thead className="bg-gray-50/80">
                            <tr>
                                <th className="w-10 px-4 py-3 text-left">
                                    <input
                                        type="checkbox"
                                        checked={records.length > 0 && selectedIds.length === records.length}
                                        onChange={toggleSelectAll}
                                        className="rounded border-gray-300 text-[#714B67] focus:ring-[#714B67]"
                                    />
                                </th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Name</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Email</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Phone</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Is Active</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Code</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Name</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Account Type</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Is Active</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Name</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Code</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Journal Type</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Is Active</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Name</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Date</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Journal</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Partner</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Reference</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">State</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Total Debit</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Total Credit</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Account</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Partner</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Label</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Debit</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Credit</th>
                                <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 bg-white">
                            {records.length > 0 ? (
                                records.map((record) => (
                                    <tr key={record.id} className="hover:bg-purple-50/30 transition">
                                        <td className="px-4 py-3">
                                            <input
                                                type="checkbox"
                                                checked={selectedIds.includes(record.id)}
                                                onChange={() => toggleSelectRow(record.id)}
                                                className="rounded border-gray-300 text-[#714B67] focus:ring-[#714B67]"
                                            />
                                        </td>
                            <td className="px-4 py-3 text-sm text-gray-700"><Link href={`/journal-entry-lines/${record.id}`} className="font-semibold text-gray-900 hover:text-[#714B67] transition">{record.name || "-"}</Link></td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.email ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.phone ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.is_active ? (
                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">Active</span>
                            ) : (
                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">Inactive</span>
                            )}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.code ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700"><Link href={`/journal-entry-lines/${record.id}`} className="font-semibold text-gray-900 hover:text-[#714B67] transition">{record.name || "-"}</Link></td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.account_type ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.is_active ? (
                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">Active</span>
                            ) : (
                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">Inactive</span>
                            )}</td>
                            <td className="px-4 py-3 text-sm text-gray-700"><Link href={`/journal-entry-lines/${record.id}`} className="font-semibold text-gray-900 hover:text-[#714B67] transition">{record.name || "-"}</Link></td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.code ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.journal_type ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.is_active ? (
                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">Active</span>
                            ) : (
                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">Inactive</span>
                            )}</td>
                            <td className="px-4 py-3 text-sm text-gray-700"><Link href={`/journal-entry-lines/${record.id}`} className="font-semibold text-gray-900 hover:text-[#714B67] transition">{record.name || "-"}</Link></td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.date ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.journal_id ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.partner_id ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.reference ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.state ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.total_debit ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.total_credit ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.account_id ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.partner_id ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.label ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.debit ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.credit ?? "-"}</td>
                                        <td className="px-4 py-3 text-right whitespace-nowrap">
                                            <Link href={`/journal-entry-lines/${record.id}`} className="text-xs font-semibold text-[#714B67] hover:underline mr-3">View</Link>
                                            <Link href={`/journal-entry-lines/${record.id}/edit`} className="text-xs font-medium text-gray-600 hover:text-gray-900">Edit</Link>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={27} className="px-4 py-16 text-center text-gray-500">
                                        <div className="flex flex-col items-center justify-center">
                                            <svg className="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                            </svg>
                                            <p className="text-base font-semibold text-gray-700">No ResPartner records found</p>
                                            <p className="text-xs text-gray-400 mt-1">Try adjusting your search or filters, or create a new record.</p>
                                            <Link
                                                href="/journal-entry-lines/create"
                                                className="mt-4 rounded bg-[#714B67] hover:bg-[#5a3b52] px-4 py-1.5 text-xs font-semibold text-white shadow-sm transition"
                                            >
                                                + Create ResPartner
                                            </Link>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
