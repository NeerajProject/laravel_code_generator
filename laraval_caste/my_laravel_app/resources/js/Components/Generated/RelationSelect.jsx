import Field from "@/Components/Generated/Field";

export default function RelationSelect({ name, label, value, options = [], onChange, error }) {
    return (
        <Field label={label} error={error}>
            <select
                name={name}
                value={value}
                onChange={(event) => onChange(event.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm"
            >
                <option value="">Select {label}</option>
                {options.map((option) => (
                    <option key={option.id} value={option.id}>
                        {option.label ?? option.name ?? option.display_name ?? option.id}
                    </option>
                ))}
            </select>
        </Field>
    );
}
