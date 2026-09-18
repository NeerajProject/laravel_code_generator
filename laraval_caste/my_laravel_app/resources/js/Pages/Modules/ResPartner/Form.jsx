import { Link, useForm } from "@inertiajs/react";
import Field from "@/Components/Generated/Field";
import RelationSelect from "@/Components/Generated/RelationSelect";
import One2ManyField from "@/Components/Generated/One2ManyField";
import TextInput from "@/Components/TextInput";

export default function Form({ record, lookups = {} }) {
    const { data, setData, post, put, processing, errors } = useForm(record ?? {});
    const submit = (e) => {
        e.preventDefault();
        record ? put(`/customers/${record.id}`) : post("/customers");
    };
    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="mx-auto max-w-5xl">
                <div className="mb-6 flex items-center justify-between">
                    <div><p className="text-sm text-gray-500">Sales / Orders</p><h1 className="text-2xl font-semibold text-gray-900">{record ? "Edit" : "Create"} ResPartner</h1></div>
                    <Link href="/customers" className="text-sm font-medium text-indigo-600 hover:text-indigo-900">Back to list</Link>
                </div>
                <form onSubmit={submit} className="space-y-6">
                    <div className="grid gap-4 md:grid-cols-2">
            <Field label="name" error={errors.name}>
                <TextInput type="text" value={data.name ?? ""} onChange={e => setData("name", e.target.value)} className="w-full" />
            </Field>
            <Field label="email" error={errors.email}>
                <TextInput type="text" value={data.email ?? ""} onChange={e => setData("email", e.target.value)} className="w-full" />
            </Field>
            <Field label="phone" error={errors.phone}>
                <TextInput type="text" value={data.phone ?? ""} onChange={e => setData("phone", e.target.value)} className="w-full" />
            </Field>
            <Field label="address" error={errors.address}>
                <textarea value={data.address ?? ""} onChange={e => setData("address", e.target.value)} className="w-full rounded-md border-gray-300 shadow-sm" rows="4" />
            </Field>
            <Field label="is_active" error={errors.is_active}>
                <TextInput type="checkbox" checked={data.is_active ?? false} onChange={e => setData("is_active", e.target.checked)} className="w-full" />
            </Field></div>
                    <div className="flex justify-end gap-3">
                        <Link href="/customers" className="rounded-md border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700">Cancel</Link>
                        <button type="submit" disabled={processing} className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow disabled:opacity-50">{processing ? "Saving..." : "Save"}</button>
                    </div>
                </form>
            </div>
        </div>
    );
}
