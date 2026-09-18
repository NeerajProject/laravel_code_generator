import Field from "@/Components/Generated/Field";

export default function One2ManyField({ name, label, value, onChange, columns = [], error }) {
    const lines = Array.isArray(value) ? value : [];
    const fields = columns.length > 0 ? columns : [{ name: "name", label: "Name", type: "text" }];

    const addLine = () => onChange([...lines, Object.fromEntries(fields.map((field) => [field.name, field.defaultValue ?? ""]))]);
    const removeLine = (index) => onChange(lines.filter((_, lineIndex) => lineIndex !== index));
    const updateLine = (index, field, fieldValue) => onChange(
        lines.map((line, lineIndex) => lineIndex === index ? { ...line, [field]: fieldValue } : line),
    );

    return (
        <Field label={label} error={error} className="md:col-span-2">
            <div className="mb-3 flex justify-end">
                <button type="button" onClick={addLine} className="rounded-md bg-gray-100 px-3 py-1 text-sm font-semibold text-gray-700">
                    Add line
                </button>
            </div>
            <div className="space-y-3">
                {lines.map((line, index) => (
                    <div key={line.id ?? index} className="rounded border border-gray-100 p-3">
                        <div className="grid gap-3 md:grid-cols-2">
                            {fields.map((field) => (
                                <label key={field.name} className="block">
                                    <span className="mb-1 block text-xs font-medium text-gray-600">{field.label ?? field.name}</span>
                                    {field.type === "select" ? (
                                        <select
                                            value={line[field.name] ?? ""}
                                            onChange={(event) => updateLine(index, field.name, event.target.value)}
                                            className="w-full rounded-md border-gray-300 shadow-sm"
                                        >
                                            <option value="">Select {field.label ?? field.name}</option>
                                            {(field.options ?? []).map((option) => (
                                                <option key={option.id} value={option.id}>{option.label ?? option.name ?? option.id}</option>
                                            ))}
                                        </select>
                                    ) : (
                                        <input
                                            type={field.type ?? "text"}
                                            value={line[field.name] ?? ""}
                                            onChange={(event) => updateLine(index, field.name, event.target.value)}
                                            className="w-full rounded-md border-gray-300 shadow-sm"
                                        />
                                    )}
                                </label>
                            ))}
                        </div>
                        <button type="button" onClick={() => removeLine(index)} className="mt-3 text-sm font-medium text-red-600">
                            Remove line
                        </button>
                    </div>
                ))}
            </div>
        </Field>
    );
}
