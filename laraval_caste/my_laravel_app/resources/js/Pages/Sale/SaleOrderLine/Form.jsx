import React from 'react';
import { Head, Link, useForm } from '@inertiajs/react';

export default function Form({ record, relations = {}, readonly = false }) {
    const isEdit = !!record?.id;

    const { data, setData, post, put, processing } = useForm({
        product_id: record?.product_id ?? record?.product?.id ?? '',
        quantity: record?.quantity ?? '',
        unit_price: record?.unit_price ?? '',
        subtotal: record?.subtotal ?? '',
    });

    const submit = (e) => {
        e.preventDefault();
        if (isEdit) {
            put(`$/sale-order-lines/${record.id}`);
        } else {
            post('/sale-order-lines');
        }
    };

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <Head title="Sale Order Line" />
            <div className="flex justify-between mb-6">
                <h1 className="text-2xl font-bold">{isEdit ? 'Edit' : 'Create'} Sale Order Line</h1>
                <Link href="/sale-order-lines" className="border px-4 py-2 rounded">Back</Link>
            </div>
            <form onSubmit={submit} className="space-y-5">

                <div>
                    <label className="block mb-1 font-medium">Product Id</label>
                    <select value={data.product_id} disabled={readonly} onChange={(e) => setData('product_id', e.target.value)} className="border rounded px-3 py-2 w-full">
                        <option value="">Select...</option>
                        {(relations['product_id'] || []).map((item) => (
                            <option key={item.id} value={item.id}>{item.name}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block mb-1 font-medium">Quantity</label>
                    <input type="number" value={data.quantity} readOnly={readonly} required={false} onChange={(e) => setData('quantity', e.target.value)} className="border rounded px-3 py-2 w-full" />
                </div>

                <div>
                    <label className="block mb-1 font-medium">Unit Price</label>
                    <input type="number" value={data.unit_price} readOnly={readonly} required={false} onChange={(e) => setData('unit_price', e.target.value)} className="border rounded px-3 py-2 w-full" />
                </div>

                <div>
                    <label className="block mb-1 font-medium">Subtotal</label>
                    <input value={data.subtotal} readOnly className="border rounded px-3 py-2 w-full bg-gray-100" />
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
