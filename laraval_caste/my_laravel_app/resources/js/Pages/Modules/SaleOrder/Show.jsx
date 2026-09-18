import { router } from "@inertiajs/react";

export default function Show({ record }) {
    return (
        <div>
            <h1>SaleOrder</h1>
            <button onClick={() => router.post("/sales/orders/${record.id}/submit")}>Submit</button>
            <div>Invoice: {record.invoice_count}</div>
            <div>Delivery: {record.delivery_count}</div>
            <pre>{JSON.stringify(record, null, 2)}</pre>
        </div>
    );
}
