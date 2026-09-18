import { Link, router } from "@inertiajs/react";
import { useState } from "react";

export default function Index({ records }) {
    const [filters, setFilters] = useState({});
    const applyFilters = () => router.get("/sales/order-lines", { filters }, { preserveState: true });

    return (
        <div>
            <h1>OrderLine</h1>
            <div>
            <input placeholder="order_id" onChange={e => setFilters({ ...filters, order_id: e.target.value })} />
            <input placeholder="product_name" onChange={e => setFilters({ ...filters, product_name: e.target.value })} />
                <button onClick={applyFilters}>Filter</button>
            </div>
            <Link href="/sales/order-lines/create">Create</Link>
            <table>
                <thead><tr>
                        <th>order_id</th>
                        <th>product_name</th>
                        <th>quantity</th>
                        <th>price_unit</th>
                        <th>subtotal</th>
                    </tr></thead>
                <tbody>
                    {records.map(record => (
                        <tr key={record.id}>
                        <td>{record.order_id}</td>
                        <td>{record.product_name}</td>
                        <td>{record.quantity}</td>
                        <td>{record.price_unit}</td>
                        <td>{record.subtotal}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
