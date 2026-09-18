import { Link, router } from "@inertiajs/react";
import { useState } from "react";

export default function Index({ records = [] }) {
    const [filters, setFilters] = useState({});
    const applyFilters = () => router.get("/products", { filters }, { preserveState: true });

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="mx-auto max-w-7xl">
                <div className="mb-6 flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-semibold text-gray-900">ProductProduct</h1>
                    </div>
                    <Link href="/products/create" className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-indigo-700">Create</Link>
                </div>
                <div className="mb-6 rounded-lg bg-white p-4 shadow">
                    <div className="grid gap-4 md:grid-cols-3">
                    <label className="block">
                        <span className="mb-1 block text-sm font-medium text-gray-700">name</span>
                        <input
                            className="w-full rounded-md border-gray-300 shadow-sm"
                            value={filters.name ?? ""}
                            onChange={e => setFilters({ ...filters, name: e.target.value })}
                        />
                    </label>
                    <label className="block">
                        <span className="mb-1 block text-sm font-medium text-gray-700">code</span>
                        <input
                            className="w-full rounded-md border-gray-300 shadow-sm"
                            value={filters.code ?? ""}
                            onChange={e => setFilters({ ...filters, code: e.target.value })}
                        />
                    </label></div>
                    <div className="mt-4 flex gap-2">
                        <button onClick={applyFilters} className="rounded-md bg-gray-900 px-4 py-2 text-sm font-semibold text-white">Apply Filters</button>
                        <button onClick={() => setFilters({})} className="rounded-md border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700">Clear</button>
                    </div>
                </div>
                <div className="overflow-hidden rounded-lg bg-white shadow">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50"><tr>
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">name</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">code</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">list_price</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">is_active</th>
                            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-gray-500">Actions</th>
                        </tr></thead>
                        <tbody className="divide-y divide-gray-100">
                            {records.map(record => (
                                <tr key={record.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-sm text-gray-700">{record.name ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.code ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.list_price ?? "-"}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{record.is_active ?? "-"}</td>
                                    <td className="px-4 py-3 text-right">
                                        <Link href={`/products/${record.id}`} className="font-medium text-indigo-600 hover:text-indigo-900">View</Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
