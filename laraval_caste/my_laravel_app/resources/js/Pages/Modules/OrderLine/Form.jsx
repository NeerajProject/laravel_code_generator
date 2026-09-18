import { useForm } from "@inertiajs/react";

export default function Form({ record }) {
    const { data, setData, post, put, processing } = useForm(record ?? {});
    const submit = (e) => {
        e.preventDefault();
        record ? put(`/sales/order-lines/${record.id}`) : post("/sales/order-lines");
    };
    return (
        <form onSubmit={submit}>
            <h1>OrderLine</h1>
            <div>
                <label>order_id</label>
                <input type="text" value={data.order_id ?? ""} onChange={e => setData("order_id", e.target.value)} />
            </div>
            <div>
                <label>product_name</label>
                <input type="text" value={data.product_name ?? ""} onChange={e => setData("product_name", e.target.value)} />
            </div>
            <div>
                <label>quantity</label>
                <input type="number" value={data.quantity ?? ""} onChange={e => setData("quantity", e.target.value)} />
            </div>
            <div>
                <label>price_unit</label>
                <input type="number" value={data.price_unit ?? ""} onChange={e => setData("price_unit", e.target.value)} />
            </div>
            <div>
                <label>subtotal</label>
                <input type="number" value={data.subtotal ?? ""} onChange={e => setData("subtotal", e.target.value)} />
            </div>
            <button type="submit" disabled={processing}>Save</button>
        </form>
    );
}
