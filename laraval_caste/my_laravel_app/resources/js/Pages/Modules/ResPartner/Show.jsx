import { Link, router } from "@inertiajs/react";

export default function Show({ record }) {
    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="mx-auto max-w-5xl">
                <div className="mb-6 flex items-center justify-between">
                    <div><p className="text-sm text-gray-500">Sales / Orders</p><h1 className="text-2xl font-semibold text-gray-900">ResPartner</h1></div>
                    <div className="flex gap-2"><Link href={`/customers/${record.id}/edit`} className="rounded-md border border-gray-300 px-3 py-2 text-sm font-semibold text-gray-700">Edit</Link></div>
                </div>
                <div className="mb-6 grid gap-4 md:grid-cols-1">
                    <div className="rounded-lg border border-gray-200 bg-white px-4 py-3 shadow-sm"><p className="text-xs uppercase tracking-wide text-gray-500">sale_order</p><p className="text-xl font-semibold text-gray-900">{record.sale_order_count ?? 0}</p></div></div>
                <div className="rounded-lg bg-white p-6 shadow"><dl className="grid gap-x-8 md:grid-cols-2">
                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">name</dt><dd className="mt-1 text-sm text-gray-900">{record.name ?? "-"}</dd></div>
                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">email</dt><dd className="mt-1 text-sm text-gray-900">{record.email ?? "-"}</dd></div>
                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">phone</dt><dd className="mt-1 text-sm text-gray-900">{record.phone ?? "-"}</dd></div>
                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">address</dt><dd className="mt-1 text-sm text-gray-900">{record.address ?? "-"}</dd></div>
                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">is_active</dt><dd className="mt-1 text-sm text-gray-900">{record.is_active ?? "-"}</dd></div></dl></div>
            </div>
        </div>
    );
}
