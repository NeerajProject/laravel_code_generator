import React from 'react';
import { Head, Link, useForm } from '@inertiajs/react';

export default function Form({ record, relations = {}, readonly = false }) {
    const isEdit = !!record?.id;

    const { data, setData, post, put, processing, errors } = useForm({
        name: record?.name ?? '',
    });

    const submit = (e) => {
        e.preventDefault();
        if (isEdit) {
            put(`/hr-employees/${record.id}`);
        } else {
            post('/hr-employees');
        }
    };

    return (
        <div className="min-h-screen bg-slate-50">
            <Head title="Hr Employee" />

            {/* Page Header */}
            <div className="bg-white border-b border-slate-200">
                <div className="max-w-5xl mx-auto px-6 py-5">
                    <div className="flex items-center justify-between flex-wrap gap-3">
                        <div>
                            <nav className="text-xs text-slate-500 mb-1">
                                <Link href="/hr-employees" className="hover:text-slate-700">Home</Link>
                                <span className="mx-1.5">/</span>
                                <Link href="/hr-employees" className="hover:text-slate-700">Hr Employee</Link>
                                <span className="mx-1.5">/</span>
                                <span className="text-slate-700 font-medium">{isEdit ? 'Edit' : 'New'}</span>
                            </nav>
                            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">
                                {isEdit ? 'Edit' : 'New'} Hr Employee
                            </h1>
                        </div>
                        <Link href="/hr-employees" className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
                            Back
                        </Link>
                    </div>
                </div>
            </div>

            <form onSubmit={submit} className="max-w-5xl mx-auto px-6 py-6 space-y-6">
                {/* Details Section */}
                <div className="bg-white rounded-lg shadow-sm border border-slate-200">
                    <div className="px-6 py-4 border-b border-slate-200 flex items-center gap-3">
                        <div className="w-8 h-8 rounded-md bg-blue-50 flex items-center justify-center">
                            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                        </div>
                        <div>
                            <h2 className="text-sm font-semibold text-slate-800">Details</h2>
                            <p className="text-xs text-slate-500">Basic information about this record</p>
                        </div>
                    </div>
                    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-x-5 gap-y-5">

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Name</label>
                            <input type="text"   value={data.name} readOnly={readonly} onChange={(e) => setData('name', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50" />
                            {errors.name && <p className="mt-1 text-xs text-rose-600">{errors.name}</p>}
                        </div>
                    </div>
                </div>

                {/* Actions */}
                {!readonly && (
                    <div className="bg-white rounded-lg shadow-sm border border-slate-200 px-6 py-4 flex items-center justify-between flex-wrap gap-3 sticky bottom-4">
                        <p className="text-xs text-slate-500">
                            Fields marked <span className="text-rose-500">*</span> are required
                        </p>
                        <div className="flex items-center gap-2">
                            <Link href="/hr-employees" className="inline-flex items-center px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">Cancel</Link>
                            <button type="submit" disabled={processing} className="inline-flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white bg-blue-600 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40 disabled:opacity-60 disabled:cursor-not-allowed transition">
                                {processing && (
                                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg>
                                )}
                                {isEdit ? 'Update' : 'Save'}
                            </button>
                        </div>
                    </div>
                )}
            </form>
        </div>
    );
}
