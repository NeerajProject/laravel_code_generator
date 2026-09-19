import React from 'react';
import { useForm, Link, router } from '@inertiajs/react';

export default function Form({ record }) {
    const isEdit = Boolean(record?.id);

    const { data, setData, post, put, processing, errors } = useForm({
        name: record?.name || '',
        date: record?.date || '',
        resPartner: record?.res?.partner || '',
        email: record?.email || '',
        isCompany: record?.is_company || '',
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (isEdit) {
            put(`/partners/${record.id}`);
        } else {
            post(`/partners`);
        }
    };

    return (
        <div className="p-6 max-w-4xl mx-auto">
            {/* Top Bar Header Actions & Smart Buttons */}
            {isEdit && (
                <div className="flex justify-between items-center bg-white p-4 rounded shadow mb-6">
                    <div className="flex space-x-2">
                <button
                    type="button"
                    onClick={() => router.post(\`/partners/\${record?.id}/confirm\`)}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1 rounded text-sm shadow"
                >
                    Confirm
                </button>
                <button
                    type="button"
                    onClick={() => router.post(\`/partners/\${record?.id}/cancel\`)}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1 rounded text-sm shadow"
                >
                    Cancel
                </button>
                <button
                    type="button"
                    onClick={() => router.post(\`/partners/\${record?.id}/validate\`)}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1 rounded text-sm shadow"
                >
                    Validate
                </button>
                    </div>
                    <div className="flex space-x-2">
                <button
                    type="button"
                    onClick={() => router.get(\`/partners/\${record?.id}/invoices\`)}
                    className="border border-gray-300 hover:bg-gray-100 text-gray-700 px-3 py-1 rounded text-sm shadow-sm"
                >
                    📊 Invoices
                </button>
                <button
                    type="button"
                    onClick={() => router.get(\`/partners/\${record?.id}/orders\`)}
                    className="border border-gray-300 hover:bg-gray-100 text-gray-700 px-3 py-1 rounded text-sm shadow-sm"
                >
                    📊 Orders
                </button>
                    </div>
                </div>
            )}

            {/* Form Card */}
            <div className="bg-white p-6 rounded shadow">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold">
                        {isEdit ? \`Edit SaleOrder #\${record.id}\` : 'Create SaleOrder'}
                    </h2>
                    <Link href="/partners" className="text-gray-600 hover:underline text-sm">
                        ← Back to list
                    </Link>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                    <input
                        type="text"
                        value={data.name}
                        onChange={(e) => setData('name', e.target.value)}
                        className="w-full border-gray-300 rounded shadow-sm focus:ring focus:ring-blue-200"
                    />
                    {errors.name && <span className="text-red-500 text-xs">{errors.name}</span>}
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                    <input
                        type="date"
                        value={data.date}
                        onChange={(e) => setData('date', e.target.value)}
                        className="w-full border-gray-300 rounded shadow-sm focus:ring focus:ring-blue-200"
                    />
                    {errors.date && <span className="text-red-500 text-xs">{errors.date}</span>}
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">ResPartner</label>
                    <input
                        type="text"
                        value={data.res.partner}
                        onChange={(e) => setData('res.partner', e.target.value)}
                        className="w-full border-gray-300 rounded shadow-sm focus:ring focus:ring-blue-200"
                    />
                    {errors.res.partner && <span className="text-red-500 text-xs">{errors.res.partner}</span>}
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Name:char*</label>
                    <input
                        type="text"
                        value={data.name:char*}
                        onChange={(e) => setData('name:char*', e.target.value)}
                        className="w-full border-gray-300 rounded shadow-sm focus:ring focus:ring-blue-200"
                    />
                    {errors.name:char* && <span className="text-red-500 text-xs">{errors.name:char*}</span>}
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email:char</label>
                    <input
                        type="text"
                        value={data.email:char}
                        onChange={(e) => setData('email:char', e.target.value)}
                        className="w-full border-gray-300 rounded shadow-sm focus:ring focus:ring-blue-200"
                    />
                    {errors.email:char && <span className="text-red-500 text-xs">{errors.email:char}</span>}
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">IsCompany:boolean</label>
                    <input
                        type="text"
                        value={data.is_company:boolean}
                        onChange={(e) => setData('is_company:boolean', e.target.value)}
                        className="w-full border-gray-300 rounded shadow-sm focus:ring focus:ring-blue-200"
                    />
                    {errors.is_company:boolean && <span className="text-red-500 text-xs">{errors.is_company:boolean}</span>}
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                    <input
                        type="text"
                        value={data.name}
                        onChange={(e) => setData('name', e.target.value)}
                        className="w-full border-gray-300 rounded shadow-sm focus:ring focus:ring-blue-200"
                    />
                    {errors.name && <span className="text-red-500 text-xs">{errors.name}</span>}
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                        type="text"
                        value={data.email}
                        onChange={(e) => setData('email', e.target.value)}
                        className="w-full border-gray-300 rounded shadow-sm focus:ring focus:ring-blue-200"
                    />
                    {errors.email && <span className="text-red-500 text-xs">{errors.email}</span>}
                </div>

                    <div className="flex justify-end space-x-2 pt-4">
                        <Link
                            href="/partners"
                            className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded"
                        >
                            Cancel
                        </Link>
                        <button
                            type="submit"
                            disabled={processing}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow"
                        >
                            {processing ? 'Saving...' : 'Save Record'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
