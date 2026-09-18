import { Link, router } from "@inertiajs/react";

export default function Show({ record }) {
    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="mx-auto max-w-5xl">
                <div className="mb-6 flex items-center justify-between">
                    <h1 className="text-2xl font-semibold text-gray-900">ProductProduct</h1>
                    <div className="flex gap-2">
                        <Link href={`/products/${record.id}/edit`} className="rounded-md border border-gray-300 px-3 py-2 text-sm font-semibold text-gray-700">Edit</Link>
                    </div>
                </div>
                <div className="mb-6 grid gap-4 md:grid-cols-1"></div>
                <div className="rounded-lg bg-white p-6 shadow"><dl className="grid gap-x-8 md:grid-cols-2">
                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">name</dt><dd className="mt-1 text-sm text-gray-900">{record.name ?? "-"}</dd></div>
                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">code</dt><dd className="mt-1 text-sm text-gray-900">{record.code ?? "-"}</dd></div>
                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">list_price</dt><dd className="mt-1 text-sm text-gray-900">{record.list_price ?? "-"}</dd></div>
                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">standard_price</dt><dd className="mt-1 text-sm text-gray-900">{record.standard_price ?? "-"}</dd></div>
                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">description</dt><dd className="mt-1 text-sm text-gray-900">{record.description ?? "-"}</dd></div>
                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">is_active</dt><dd className="mt-1 text-sm text-gray-900">{record.is_active ?? "-"}</dd></div></dl></div>
            </div>
        </div>
    );
}
