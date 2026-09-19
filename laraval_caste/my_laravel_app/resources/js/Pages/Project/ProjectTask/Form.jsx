import React from 'react';
import { Head, Link, useForm } from '@inertiajs/react';

export default function Form({ record, relations = {}, readonly = false }) {
    const isEdit = !!record?.id;

    const { data, setData, post, put, processing, errors } = useForm({
        name: record?.name ?? '',
        project_id: record?.project_id ?? record?.project?.id ?? '',
        assignee_id: record?.assignee_id ?? record?.assignee?.id ?? '',
        deadline: record?.deadline ?? '',
        state: record?.state ?? '',
        description: record?.description ?? '',
        timesheet_ids: record?.timesheet_ids || [],
        total_hours: record?.total_hours ?? '',
    });

    const submit = (e) => {
        e.preventDefault();
        if (isEdit) {
            put(`/project-tasks/${record.id}`);
        } else {
            post('/project-tasks');
        }
    };

    const addTimesheetIds = () => {
        setData('timesheet_ids', [
            ...(data.timesheet_ids || []),
            {
                date: '',
                task_id: '',
                employee_id: '',
                hours: '',
                description: '',
            },
        ]);
    };

    const removeTimesheetIds = (index) => {
        setData('timesheet_ids', (data.timesheet_ids || []).filter((_, i) => i !== index));
    };

    const updateTimesheetIds = (index, key, value) => {
        const copy = [...(data.timesheet_ids || [])];
        copy[index] = { ...copy[index], [key]: value };
        setData('timesheet_ids', copy);
    };

    return (
        <div className="min-h-screen bg-slate-50">
            <Head title="Project Task" />

            {/* Page Header */}
            <div className="bg-white border-b border-slate-200">
                <div className="max-w-5xl mx-auto px-6 py-5">
                    <div className="flex items-center justify-between flex-wrap gap-3">
                        <div>
                            <nav className="text-xs text-slate-500 mb-1">
                                <Link href="/project-tasks" className="hover:text-slate-700">Home</Link>
                                <span className="mx-1.5">/</span>
                                <Link href="/project-tasks" className="hover:text-slate-700">Project Task</Link>
                                <span className="mx-1.5">/</span>
                                <span className="text-slate-700 font-medium">{isEdit ? 'Edit' : 'New'}</span>
                            </nav>
                            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">
                                {isEdit ? 'Edit' : 'New'} Project Task
                            </h1>
                        </div>
                        <Link href="/project-tasks" className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">
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
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Name <span className="text-rose-500">*</span></label>
                            <input type="text"  required value={data.name} readOnly={readonly} onChange={(e) => setData('name', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50" />
                            {errors.name && <p className="mt-1 text-xs text-rose-600">{errors.name}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Project Id</label>
                            <select value={data.project_id} disabled={readonly} onChange={(e) => setData('project_id', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50">
                                <option value="">Select...</option>
                                {(relations['project_id'] || []).map((item) => (
                                    <option key={item.id} value={item.id}>{item.name}</option>
                                ))}
                            </select>
                            {errors.project_id && <p className="mt-1 text-xs text-rose-600">{errors.project_id}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Assignee Id</label>
                            <select value={data.assignee_id} disabled={readonly} onChange={(e) => setData('assignee_id', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50">
                                <option value="">Select...</option>
                                {(relations['assignee_id'] || []).map((item) => (
                                    <option key={item.id} value={item.id}>{item.name}</option>
                                ))}
                            </select>
                            {errors.assignee_id && <p className="mt-1 text-xs text-rose-600">{errors.assignee_id}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Deadline</label>
                            <input type="date"   value={data.deadline} readOnly={readonly} onChange={(e) => setData('deadline', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50" />
                            {errors.deadline && <p className="mt-1 text-xs text-rose-600">{errors.deadline}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">State</label>
                            <select value={data.state} disabled={readonly} onChange={(e) => setData('state', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50">
                                <option value="">Select...</option>
                                <option value="new">New</option>
                                <option value="in_progress">In Progress</option>
                                <option value="review">Review</option>
                                <option value="done">Done</option>
                            </select>
                            {errors.state && <p className="mt-1 text-xs text-rose-600">{errors.state}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Description</label>
                            <textarea value={data.description} readOnly={readonly} onChange={(e) => setData('description', e.target.value)} rows="4" className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-3 py-2 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50" />
                            {errors.description && <p className="mt-1 text-xs text-rose-600">{errors.description}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Total Hours</label>
                            <input value={data.total_hours} readOnly className="w-full text-sm font-medium text-slate-800 bg-slate-50 border border-slate-200 rounded-md px-3 py-2" />
                            {errors.total_hours && <p className="mt-1 text-xs text-rose-600">{errors.total_hours}</p>}
                        </div>
                    </div>
                </div>

                {/* Line Items */}
                <div className="bg-white rounded-lg shadow-sm border border-slate-200">
                    <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-md bg-indigo-50 flex items-center justify-center">
                                <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" /></svg>
                            </div>
                            <div>
                                <h2 className="text-sm font-semibold text-slate-800">Timesheet Ids</h2>
                                <p className="text-xs text-slate-500">Add one or more line items</p>
                            </div>
                        </div>
                        {!readonly && (
                            <button type="button" onClick={addTimesheetIds} className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-md transition">
                                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                                Add Line
                            </button>
                        )}
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="bg-slate-50 border-b border-slate-200">
                                    <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Date</th>
                                    <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Task Id</th>
                                    <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Employee Id</th>
                                    <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Hours</th>
                                    <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Description</th>
                                    <th className="w-14 px-3 py-2.5"></th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {(data.timesheet_ids || []).length === 0 ? (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-10 text-center">
                                            <div className="flex flex-col items-center gap-2 text-slate-400">
                                                <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                                                <p className="text-xs">No lines added yet. Click "Add Line" to begin.</p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : (data.timesheet_ids || []).map((line, index) => (
                                    <tr key={index} className="hover:bg-slate-50/60">
                                        <td className="px-4 py-2.5 align-top">
                                            <input type="date"  value={line.date ?? ''} disabled={readonly} onChange={(e) => updateTimesheetIds(index, 'date', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-2.5 py-1.5 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500" />
                                        </td>
                                        <td className="px-4 py-2.5 align-top">
                                            <select value={line.task_id ?? ''} disabled={readonly} onChange={(e) => updateTimesheetIds(index, 'task_id', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-2.5 py-1.5 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500">
                                                <option value="">Select...</option>
                                                {(relations['task_id'] || []).map((item) => (
                                                    <option key={item.id} value={item.id}>{item.name}</option>
                                                ))}
                                            </select>
                                        </td>
                                        <td className="px-4 py-2.5 align-top">
                                            <select value={line.employee_id ?? ''} disabled={readonly} onChange={(e) => updateTimesheetIds(index, 'employee_id', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-2.5 py-1.5 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500">
                                                <option value="">Select...</option>
                                                {(relations['employee_id'] || []).map((item) => (
                                                    <option key={item.id} value={item.id}>{item.name}</option>
                                                ))}
                                            </select>
                                        </td>
                                        <td className="px-4 py-2.5 align-top">
                                            <input type="number" step="0.01" value={line.hours ?? ''} disabled={readonly} onChange={(e) => updateTimesheetIds(index, 'hours', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-2.5 py-1.5 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500" />
                                        </td>
                                        <td className="px-4 py-2.5 align-top">
                                            <input type="text"  value={line.description ?? ''} disabled={readonly} onChange={(e) => updateTimesheetIds(index, 'description', e.target.value)} className="w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md px-2.5 py-1.5 placeholder:text-slate-400 transition focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-500" />
                                        </td>
                                        <td className="px-3 py-2.5 text-center align-middle">
                                            {!readonly && (
                                                <button type="button" onClick={() => removeTimesheetIds(index)} className="inline-flex items-center justify-center w-8 h-8 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-md transition" title="Remove">
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M9 7V4a1 1 0 011-1h4a1 1 0 011 1v3" /></svg>
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Actions */}
                {!readonly && (
                    <div className="bg-white rounded-lg shadow-sm border border-slate-200 px-6 py-4 flex items-center justify-between flex-wrap gap-3 sticky bottom-4">
                        <p className="text-xs text-slate-500">
                            Fields marked <span className="text-rose-500">*</span> are required
                        </p>
                        <div className="flex items-center gap-2">
                            <Link href="/project-tasks" className="inline-flex items-center px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">Cancel</Link>
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
