import React, { useState } from 'react';
import { Head, Link, router } from '@inertiajs/react';

export default function Index({ records }) {
    const [search, setSearch] = useState('');

    const submitSearch = (e) => {
        e.preventDefault();
        router.get('/sale-orders', { search }, { preserveState: true, replace: true });
    };

    const remove = (id) => {
        if (!confirm('Delete this record?')) return;
        router.delete(`$/sale-orders/${id}`);
    };

    return (
        <div className="p-6">
            <Head title="Sale Order" />
            <div className="flex justify-between mb-6">
                <h1 className="text-2xl font-bold">Sale Order</h1>
                <Link href="/sale-orders/create" className="px-4 py-2 bg-blue-600 text-white rounded">Create</Link>
            </div>
            <form onSubmit={submitSearch} className="mb-4 flex gap-2">
                <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search..." className="border rounded px-3 py-2" />
                <button className="border px-4 py-2 rounded">Search</button>
            </form>
            <div className="overflow-x-auto">
                <table className="w-full border">
                    <thead>
                        <tr>
                            <th className="border p-2 text-left">Name</th>
                            <th className="border p-2 text-left">Customer Id</th>
                            <th className="border p-2 text-left">Order Date</th>
                            <th className="border p-2 text-left">State</th>
                            <th className="border p-2 text-left">Amount Total</th>
                            <th className="border p-2">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {records.data.map((row) => (
                            <tr key={row.id}>
                                <td className="border p-2">{row.name ?? '-'}</td>
                                <td className="border p-2">{row.customer?.name || row.customer_id || '-'}</td>
                                <td className="border p-2">{row.order_date ?? '-'}</td>
                                <td className="border p-2">{row.state ?? '-'}</td>
                                <td className="border p-2">{row.amount_total ?? '-'}</td>
                                <td className="border p-2">
                                    <Link href={`/sale-orders/${row.id}/edit`} className="mr-3 text-blue-600">Edit</Link>
                                    <button onClick={() => remove(row.id)} className="text-red-600">Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
