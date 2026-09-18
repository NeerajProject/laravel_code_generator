import React from 'react';
import { Head, Link, useForm } from '@inertiajs/react';

export default function Form({ record, relations = {}, readonly = false }) {
    const isEdit = !!record?.id;

    const { data, setData, post, put, processing } = useForm({
        name: record?.name ?? '',
    });

    const submit = (e) => {
        e.preventDefault();
        if (isEdit) {
            put(`$/product-products/${record.id}`);
        } else {
            post('/product-products');
        }
    };

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <Head title="Product Product" />
            <div className="flex justify-between mb-6">
                <h1 className="text-2xl font-bold">{isEdit ? 'Edit' : 'Create'} Product Product</h1>
                <Link href="/product-products" className="border px-4 py-2 rounded">Back</Link>
            </div>
            <form onSubmit={submit} className="space-y-5">

                <div>
                    <label className="block mb-1 font-medium">Name</label>
                    <input type="text" value={data.name} readOnly={readonly} required={false} onChange={(e) => setData('name', e.target.value)} className="border rounded px-3 py-2 w-full" />
                </div>

                {!readonly && (
                    <button type="submit" disabled={processing} className="px-5 py-2 bg-blue-600 text-white rounded">
                        {isEdit ? 'Update' : 'Save'}
                    </button>
                )}
            </form>
        </div>
    );
}
