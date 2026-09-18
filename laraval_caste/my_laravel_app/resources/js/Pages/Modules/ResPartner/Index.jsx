import { Link, router } from "@inertiajs/react";
import { useState } from "react";

export default function Index({ records }) {
    const [filters, setFilters] = useState({});
    const applyFilters = () => router.get("/customers", { filters }, { preserveState: true });

    return (
        <div>
            <h1>ResPartner</h1>
            <div>
            <input placeholder="name" onChange={e => setFilters({ ...filters, name: e.target.value })} />
            <input placeholder="email" onChange={e => setFilters({ ...filters, email: e.target.value })} />
            <input placeholder="phone" onChange={e => setFilters({ ...filters, phone: e.target.value })} />
                <button onClick={applyFilters}>Filter</button>
            </div>
            <Link href="/customers/create">Create</Link>
            <table>
                <thead><tr>
                        <th>name</th>
                        <th>email</th>
                        <th>phone</th>
                        <th>is_active</th>
                    </tr></thead>
                <tbody>
                    {records.map(record => (
                        <tr key={record.id}>
                        <td>{record.name}</td>
                        <td>{record.email}</td>
                        <td>{record.phone}</td>
                        <td>{record.is_active}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
