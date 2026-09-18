import { router } from "@inertiajs/react";

export default function Show({ record }) {
    return (
        <div>
            <h1>ResPartner</h1>
            <div>Sale_Order: {record.sale_order_count}</div>
            <pre>{JSON.stringify(record, null, 2)}</pre>
        </div>
    );
}
