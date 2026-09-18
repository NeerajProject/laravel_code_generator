import React from 'react';
import { Link, router } from '@inertiajs/react';

export default function Index({ records }) {
    const handleDelete = (id) => {
        if (confirm('Are you sure you want to delete this record?')) {
            router.delete(`/partners/${id}`);
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">SaleOrder List</h1>
                <Link
                    href="/partners/create"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow"
                >
                    + Create New
                </Link>
            </div>

            <div className="bg-white shadow rounded-lg overflow-hidden">
                <table className="min-w-full text-sm text-gray-700">
                    <thead className="bg-gray-100 font-semibold">
                        <tr>
                            <th className="px-4 py-2 border-b text-left">ID</th>
                <th className="px-4 py-2 border-b text-left">Name</th>
                <th className="px-4 py-2 border-b text-left">Date</th>
                <th className="px-4 py-2 border-b text-left">Name</th>
                <th className="px-4 py-2 border-b text-left">Email</th>
                            <th className="px-4 py-2 border-b text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {records?.data?.length > 0 ? (
                            records.data.map((row) => (
                                <tr key={row.id} className="hover:bg-gray-50 border-b">
                                    <td className="px-4 py-2">{row.id}</td>
                <td className="px-4 py-2 border-b">{row.name}</td>
                <td className="px-4 py-2 border-b">{row.date}</td>
                <td className="px-4 py-2 border-b">{row.name}</td>
                <td className="px-4 py-2 border-b">{row.email}</td>
                                    <td className="px-4 py-2 text-right space-x-2">
                                        <Link
                                            href={\`/partners/\${row.id}/edit\`}
                                            className="text-indigo-600 hover:underline"
                                        >
                                            Edit
                                        </Link>
                                        <button
                                            onClick={() => handleDelete(row.id)}
                                            className="text-red-600 hover:underline ml-2"
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="6" className="text-center py-6 text-gray-500">
                                    No records found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
