import React from 'react';
import { Head, Link, useForm } from '@inertiajs/react';

export default function Form({ record, relations = {}, readonly = false }) {
    const isEdit = !!record?.id;

    const { data, setData, post, put, processing } = useForm({
        name: record?.name ?? '',
        customer_id: record?.customer_id ?? record?.customer?.id ?? '',
        order_date: record?.order_date ?? '',
        state: record?.state ?? '',
        order_line_ids: record?.order_line_ids || [],
        note: record?.note ?? '',
        amount_total: record?.amount_total ?? '',
    });

    const submit = (e) => {
        e.preventDefault();
        if (isEdit) {
            put(`$/sale-orders/${record.id}`);
        } else {
            post('/sale-orders');
        }
    };

    const addOrderLineIds = () => {
        setData('order_line_ids', [...(data.order_line_ids || []), {
            product_id: '',
            quantity: '',
            unit_price: '',
        }]);
    };

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <Head title="Sale Order" />
            <div className="flex justify-between mb-6">
                <h1 className="text-2xl font-bold">{isEdit ? 'Edit' : 'Create'} Sale Order</h1>
                <Link href="/sale-orders" className="border px-4 py-2 rounded">Back</Link>
            </div>
            <form onSubmit={submit} className="space-y-5">

                <div>
                    <label className="block mb-1 font-medium">Name</label>
                    <input type="text" value={data.name} readOnly={readonly} required={true} onChange={(e) => setData('name', e.target.value)} className="border rounded px-3 py-2 w-full" />
                </div>

                <div>
                    <label className="block mb-1 font-medium">Customer Id</label>
                    <select value={data.customer_id} disabled={readonly} onChange={(e) => setData('customer_id', e.target.value)} className="border rounded px-3 py-2 w-full">
                        <option value="">Select...</option>
                        {(relations['customer_id'] || []).map((item) => (
                            <option key={item.id} value={item.id}>{item.name}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block mb-1 font-medium">Order Date</label>
                    <input type="date" value={data.order_date} readOnly={readonly} required={false} onChange={(e) => setData('order_date', e.target.value)} className="border rounded px-3 py-2 w-full" />
                </div>

                <div>
                    <label className="block mb-1 font-medium">State</label>
                    <select value={data.state} disabled={readonly} onChange={(e) => setData('state', e.target.value)} className="border rounded px-3 py-2 w-full">
                        <option value="">Select...</option>
                        <option value="draft">Draft</option>
                        <option value="confirmed">Confirmed</option>
                        <option value="cancelled">Cancelled</option>
                    </select>
                </div>

                <div className="border rounded p-4">
                    <div className="flex justify-between mb-3">
                        <h2 className="font-semibold">Order Line Ids</h2>
                        {!readonly && <button type="button" onClick={addOrderLineIds} className="border px-3 py-1 rounded">Add Line</button>}
                    </div>
                    {(data.order_line_ids || []).map((line, index) => (
                        <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
                            <select value={line.product_id ?? ''} disabled={readonly} onChange={(e) => { const copy = [...data.order_line_ids]; copy[index] = { ...copy[index], product_id: e.target.value }; setData('order_line_ids', copy); }} className="border rounded px-2 py-1">
                                <option value="">Product Id</option>
                                {(relations['product_id'] || []).map((item) => (
                                    <option key={item.id} value={item.id}>{item.name}</option>
                                ))}
                            </select>
                            <input type="number" value={line.quantity ?? ''} disabled={readonly} onChange={(e) => { const copy = [...data.order_line_ids]; copy[index] = { ...copy[index], quantity: e.target.value }; setData('order_line_ids', copy); }} className="border rounded px-2 py-1" placeholder="Quantity" />
                            <input type="number" value={line.unit_price ?? ''} disabled={readonly} onChange={(e) => { const copy = [...data.order_line_ids]; copy[index] = { ...copy[index], unit_price: e.target.value }; setData('order_line_ids', copy); }} className="border rounded px-2 py-1" placeholder="Unit Price" />
                            <input value={line.subtotal ?? ''} readOnly className="border rounded px-2 py-1 bg-gray-100" placeholder="Subtotal" />
                        </div>
                    ))}
                </div>

                <div>
                    <label className="block mb-1 font-medium">Note</label>
                    <textarea value={data.note} readOnly={readonly} onChange={(e) => setData('note', e.target.value)} className="border rounded px-3 py-2 w-full" rows="4" />
                </div>

                <div>
                    <label className="block mb-1 font-medium">Amount Total</label>
                    <input value={data.amount_total} readOnly className="border rounded px-3 py-2 w-full bg-gray-100" />
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
