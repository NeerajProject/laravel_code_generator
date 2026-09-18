import { router } from "@inertiajs/react";

export default function Show({ record }) {
    return (
        <div>
            <h1>OrderLine</h1>
            <pre>{JSON.stringify(record, null, 2)}</pre>
        </div>
    );
}
