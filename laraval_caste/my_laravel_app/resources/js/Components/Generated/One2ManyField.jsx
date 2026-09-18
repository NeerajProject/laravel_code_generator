import React from "react";

export default function One2ManyField({
    name,
    label = "Lines",
    value = [],
    onChange,
    columns = [
        { name: "name", label: "Title", type: "text" },
        { name: "description", label: "Description", type: "text" },
        { name: "is_done", label: "Done", type: "bool" },
    ],
    error,
}) {
    const lines = Array.isArray(value) ? value : [];

    const addLine = () => {
        const newLine = {};
        columns.forEach((col) => {
            newLine[col.name] = col.defaultValue ?? (col.type === "bool" ? false : (col.type === "number" ? 0 : ""));
        });
        onChange([...lines, newLine]);
    };

    const removeLine = (index) => {
        onChange(lines.filter((_, i) => i !== index));
    };

    const updateLine = (index, colName, val) => {
        const next = lines.map((line, i) => {
            if (i === index) {
                return { ...line, [colName]: val };
            }
            return line;
        });
        onChange(next);
    };

    return (
        <div className="w-full">
            <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    {label} ({lines.length})
                </span>
            </div>

            <div className="border border-gray-200 rounded overflow-hidden shadow-sm bg-white">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                    <thead className="bg-gray-50/80">
                        <tr>
                            <th className="w-12 px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">#</th>
                            {columns.map((col) => (
                                <th
                                    key={col.name}
                                    className={`px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider ${
                                        col.type === "bool" ? "text-center w-24" : "text-left"
                                    }`}
                                >
                                    {col.label || col.name}
                                </th>
                            ))}
                            <th className="w-12 px-3 py-2 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider"></th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 bg-white">
                        {lines.length > 0 ? (
                            lines.map((line, index) => (
                                <tr key={line.id ?? index} className="hover:bg-gray-50/50 transition">
                                    <td className="px-3 py-2 text-xs font-mono text-gray-400">{index + 1}</td>
                                    {columns.map((col) => (
                                        <td key={col.name} className="px-3 py-1.5">
                                            {col.type === "bool" ? (
                                                <div className="flex justify-center items-center">
                                                    <input
                                                        type="checkbox"
                                                        checked={Boolean(line[col.name])}
                                                        onChange={(e) => updateLine(index, col.name, e.target.checked)}
                                                        className="rounded border-gray-300 text-[#714B67] focus:ring-[#714B67] w-4 h-4 cursor-pointer"
                                                    />
                                                </div>
                                            ) : col.type === "number" ? (
                                                <input
                                                    type="number"
                                                    value={line[col.name] ?? ""}
                                                    onChange={(e) => updateLine(index, col.name, e.target.value)}
                                                    placeholder={col.placeholder || "0"}
                                                    className="w-full text-sm rounded border-gray-200 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] py-1 px-2"
                                                />
                                            ) : (
                                                <input
                                                    type="text"
                                                    value={line[col.name] ?? ""}
                                                    onChange={(e) => updateLine(index, col.name, e.target.value)}
                                                    placeholder={col.placeholder || `${col.label || col.name}...`}
                                                    className="w-full text-sm rounded border-gray-200 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] py-1 px-2"
                                                />
                                            )}
                                        </td>
                                    ))}
                                    <td className="px-3 py-1.5 text-center">
                                        <button
                                            type="button"
                                            onClick={() => removeLine(index)}
                                            className="text-gray-400 hover:text-red-600 transition p-1 rounded hover:bg-red-50"
                                            title="Delete line"
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={columns.length + 2} className="px-4 py-8 text-center text-sm text-gray-500">
                                    No {label.toLowerCase()} added yet. Click &quot;Add a line&quot; below.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="mt-2.5">
                <button
                    type="button"
                    onClick={addLine}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#714B67] hover:text-[#5a3b52] px-3 py-1.5 rounded border border-dashed border-purple-300 hover:bg-purple-50 transition"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Add a line
                </button>
            </div>

            {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
        </div>
    );
}
