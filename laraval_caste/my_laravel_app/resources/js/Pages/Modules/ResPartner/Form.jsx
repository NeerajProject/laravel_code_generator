import { useForm } from "@inertiajs/react";

export default function Form({ record }) {
    const { data, setData, post, put, processing } = useForm(record ?? {});
    const submit = (e) => {
        e.preventDefault();
        record ? put(`/customers/${record.id}`) : post("/customers");
    };
    return (
        <form onSubmit={submit}>
            <h1>ResPartner</h1>
            <div>
                <label>name</label>
                <input type="text" value={data.name ?? ""} onChange={e => setData("name", e.target.value)} />
            </div>
            <div>
                <label>email</label>
                <input type="text" value={data.email ?? ""} onChange={e => setData("email", e.target.value)} />
            </div>
            <div>
                <label>phone</label>
                <input type="text" value={data.phone ?? ""} onChange={e => setData("phone", e.target.value)} />
            </div>
            <div>
                <label>address</label>
                <input type="text" value={data.address ?? ""} onChange={e => setData("address", e.target.value)} />
            </div>
            <div>
                <label>is_active</label>
                <input type="checkbox" value={data.is_active ?? ""} onChange={e => setData("is_active", e.target.value)} />
            </div>
            <button type="submit" disabled={processing}>Save</button>
        </form>
    );
}
