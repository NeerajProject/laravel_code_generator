import { Link, router } from "@inertiajs/react";
import { useState } from "react";

export default function Index({ records }) {
    const [filters, setFilters] = useState({});
    const applyFilters = () => router.get("/sales/orders", { filters }, { preserveState: true });

    return (
        <div>
            <h1>SaleOrder</h1>
            <div>
            <input placeholder="name" onChange={e => setFilters({ ...filters, name: e.target.value })} />
            <input placeholder="customer_id" onChange={e => setFilters({ ...filters, customer_id: e.target.value })} />
                <button onClick={applyFilters}>Filter</button>
            </div>
            <Link href="/sales/orders/create">Create</Link>
            <table>
                <thead><tr>
                        <th>name</th>
                        <th>customer_id</th>
                        <th>amount_total</th>
                    </tr></thead>
                <tbody>
                    {records.map(record => (
                        <tr key={record.id}>
                        <td>{record.name}</td>
                        <td>{record.customer_id}</td>
                        <td>{record.amount_total}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
