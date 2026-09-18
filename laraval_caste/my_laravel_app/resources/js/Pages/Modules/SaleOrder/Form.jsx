import { useForm } from "@inertiajs/react";

export default function Form({ record }) {
    const { data, setData, post, put, processing } = useForm(record ?? {});
    const submit = (e) => {
        e.preventDefault();
        record ? put(`/sales/orders/${record.id}`) : post("/sales/orders");
    };
    return (
        <form onSubmit={submit}>
            <h1>SaleOrder</h1>
            <div>
                <label>name</label>
                <input type="text" value={data.name ?? ""} onChange={e => setData("name", e.target.value)} />
            </div>
            <div>
                <label>customer_id</label>
                <input type="text" value={data.customer_id ?? ""} onChange={e => setData("customer_id", e.target.value)} />
            </div>
            <button type="submit" disabled={processing}>Save</button>
        </form>
    );
}
