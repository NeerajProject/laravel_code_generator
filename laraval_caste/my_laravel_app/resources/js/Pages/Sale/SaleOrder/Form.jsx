import React from 'react';
import { Head, Link, useForm } from '@inertiajs/react';

export default function Form({ record, relations = {}, readonly = false }) {
    const isEdit = !!record?.id;

    const { data, setData, post, put, processing, errors } = useForm({
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
            put(`/sale-orders/${record.id}`);
        } else {
            post('/sale-orders');
        }
    };

    const addOrderLineIds = () => {
        setData('order_line_ids', [
            ...(data.order_line_ids || []),
            {
                product_id: '',
                quantity: '',
                unit_price: '',
            },
        ]);
    };

    const removeOrderLineIds = (index) => {
        setData('order_line_ids', (data.order_line_ids || []).filter((_, i) => i !== index));
    };

    const updateOrderLineIds = (index, key, value) => {
        const copy = [...(data.order_line_ids || [])];
        copy[index] = { ...copy[index], [key]: value };
        setData('order_line_ids', copy);
    };

    return (
        <div className="min-h-screen bg-slate-50">
            <Head title="Sale Order" />

            {/* Page Header */}
            <div className="bg-white border-b border-slate-200">
                <div className="max-w-5xl mx-auto px-6 py-5">
                    <div className="flex items-center justify-between flex-wrap gap-3">
                        <div>
                            <nav className="text-xs text-slate-500 mb-1">
                                <Link href="/sale-orders" className="hover:text-slate-700">Home</Link>
                                <span className="mx-1.5">/</span>
                                <Link href="/sale-orders" className="hover:text-slate-700">Sale Order</Link>
                                <span className="mx-1.5">/</span>
                                <span className="text-slate-700 font-medium">{isEdit ? 'Edit' : 'New'}</span>
                            </nav>
                            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">
                                {isEdit ? 'Edit' : 'New'} Sale Order
                            </h1>
                        </div>
                        <Link href="/sale-orders" className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
                            Back
                        </Link>
                    </div>
                </div>
            </div>

            <form onSubmit={submit} className="max-w-5xl mx-auto px-6 py-6 space-y-6">
                {/* Details Section */}
                <div className="bg-white rounded-lg shadow-sm border border-slate-200">
                    <div className="px-6 py-4 border-b border-slate-200 flex items-center gap-3">
                        <div className="w-8 h-8 rounded-md bg-blue-50 flex items-center justify-center">
                            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                        </div>
                        <div>
                            <h2 className="text-sm font-semibold text-slate-800">Details</h2>
                            <p className="text-xs text-slate-500">Basic information about this record</p>
                        </div>
                    </div>
                    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-x-5 gap-y-5">

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Name <span className="text-rose-500">*</span></label>
                            <input type="text"  required value={data.name} readOnly={readonly} onChange={(e) => setData('name', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50" />
                            {errors.name && <p className="mt-1 text-xs text-rose-600">{errors.name}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Customer Id</label>
                            <select value={data.customer_id} disabled={readonly} onChange={(e) => setData('customer_id', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50">
                                <option value="">Select...</option>
                                {(relations['customer_id'] || []).map((item) => (
                                    <option key={item.id} value={item.id}>{item.name}</option>
                                ))}
                            </select>
                            {errors.customer_id && <p className="mt-1 text-xs text-rose-600">{errors.customer_id}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Order Date</label>
                            <input type="date"   value={data.order_date} readOnly={readonly} onChange={(e) => setData('order_date', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50" />
                            {errors.order_date && <p className="mt-1 text-xs text-rose-600">{errors.order_date}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">State</label>
                            <select value={data.state} disabled={readonly} onChange={(e) => setData('state', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50">
                                <option value="">Select...</option>
                                <option value="draft">Draft</option>
                                <option value="confirmed">Confirmed</option>
                                <option value="cancelled">Cancelled</option>
                            </select>
                            {errors.state && <p className="mt-1 text-xs text-rose-600">{errors.state}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Note</label>
                            <textarea value={data.note} readOnly={readonly} onChange={(e) => setData('note', e.target.value)} rows="4" className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50" />
                            {errors.note && <p className="mt-1 text-xs text-rose-600">{errors.note}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Amount Total</label>
                            <input value={data.amount_total} readOnly className="w-full text-sm font-medium text-slate-800 bg-slate-50 border border-slate-200 rounded-md px-3 py-2" />
                            {errors.amount_total && <p className="mt-1 text-xs text-rose-600">{errors.amount_total}</p>}
                        </div>
                    </div>
                </div>

                {/* Line Items */}
                <div className="bg-white rounded-lg shadow-sm border border-slate-200">
                    <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-md bg-indigo-50 flex items-center justify-center">
                                <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" /></svg>
                            </div>
                            <div>
                                <h2 className="text-sm font-semibold text-slate-800">Order Line Ids</h2>
                                <p className="text-xs text-slate-500">Add one or more line items</p>
                            </div>
                        </div>
                        {!readonly && (
                            <button type="button" onClick={addOrderLineIds} className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-md transition">
                                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                                Add Line
                            </button>
                        )}
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="bg-slate-50 border-b border-slate-200">
                                    <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Product Id</th>
                                    <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Quantity</th>
                                    <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Unit Price</th>
                                    <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Subtotal</th>
                                    <th className="w-14 px-3 py-2.5"></th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {(data.order_line_ids || []).length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-10 text-center">
                                            <div className="flex flex-col items-center gap-2 text-slate-400">
                                                <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                                                <p className="text-xs">No lines added yet. Click "Add Line" to begin.</p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : (data.order_line_ids || []).map((line, index) => (
                                    <tr key={index} className="hover:bg-slate-50/60">
                                        <td className="px-4 py-2.5 align-top">
                                            <select value={line.product_id ?? ''} disabled={readonly} onChange={(e) => updateOrderLineIds(index, 'product_id', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-2.5 py-1.5 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500">
                                                <option value="">Select...</option>
                                                {(relations['product_id'] || []).map((item) => (
                                                    <option key={item.id} value={item.id}>{item.name}</option>
                                                ))}
                                            </select>
                                        </td>
                                        <td className="px-4 py-2.5 align-top">
                                            <input type="number" step="0.01" value={line.quantity ?? ''} disabled={readonly} onChange={(e) => updateOrderLineIds(index, 'quantity', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-2.5 py-1.5 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500" />
                                        </td>
                                        <td className="px-4 py-2.5 align-top">
                                            <input type="number" step="0.01" value={line.unit_price ?? ''} disabled={readonly} onChange={(e) => updateOrderLineIds(index, 'unit_price', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-2.5 py-1.5 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500" />
                                        </td>
                                        <td className="px-4 py-2.5 align-top">
                                            <input value={line.subtotal ?? ''} readOnly className="w-full text-sm font-medium text-slate-800 bg-slate-50 border border-slate-200 rounded-md px-2.5 py-1.5" />
                                        </td>
                                        <td className="px-3 py-2.5 text-center align-middle">
                                            {!readonly && (
                                                <button type="button" onClick={() => removeOrderLineIds(index)} className="inline-flex items-center justify-center w-8 h-8 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-md transition" title="Remove">
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M9 7V4a1 1 0 011-1h4a1 1 0 011 1v3" /></svg>
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Actions */}
                {!readonly && (
                    <div className="bg-white rounded-lg shadow-sm border border-slate-200 px-6 py-4 flex items-center justify-between flex-wrap gap-3 sticky bottom-4">
                        <p className="text-xs text-slate-500">
                            Fields marked <span className="text-rose-500">*</span> are required
                        </p>
                        <div className="flex items-center gap-2">
                            <Link href="/sale-orders" className="inline-flex items-center px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">Cancel</Link>
                            <button type="submit" disabled={processing} className="inline-flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white bg-blue-600 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40 disabled:opacity-60 disabled:cursor-not-allowed transition">
                                {processing && (
                                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg>
                                )}
                                {isEdit ? 'Update' : 'Save'}
                            </button>
                        </div>
                    </div>
                )}
            </form>
        </div>
    );
}
