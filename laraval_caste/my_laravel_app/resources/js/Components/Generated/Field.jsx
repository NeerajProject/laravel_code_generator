import InputError from "@/Components/InputError";
import InputLabel from "@/Components/InputLabel";

export default function Field({ label, error, children, className = "" }) {
    return (
        <div className={`rounded-md border border-gray-200 bg-white p-4 ${className}`}>
            <InputLabel value={label} className="mb-1" />
            {children}
            <InputError message={error} className="mt-1" />
        </div>
    );
}
