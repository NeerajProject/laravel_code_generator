from pathlib import Path
from datetime import datetime

# ============================================================
# DSL (Grammar for Odoo-like modular Laravel generator)
# ============================================================

DSL = """
project:/home/nj/workspace/laravel_code_generator/laravel_code_generator/laraval_caste/my_laravel_app
module:Product

product.product
url:/products

name:char*
code:char
list_price:float
standard_price:float
description:text
is_active:bool

list:
    name
    code
    list_price
    is_active

filter:
    name
    code

form:
    name
    code
    list_price
    standard_price
    description
    is_active

menu:
    Sales/Products
"""

# ============================================================
# HELPERS
# ============================================================

def class_name(model):
    """sale.order -> SaleOrder"""
    return "".join(part.capitalize() for part in model.split("."))

def table_name(model):
    """sale.order -> sale_orders"""
    return model.replace(".", "_") + "s"

def namespace(model, module_name=None):
    """sale.order -> App\\Modules\\Product"""
    return f"App\\Modules\\{module_name or class_name(model)}"

def relation_model(field_type):
    """m2o(res.partner) -> ResPartner"""
    if "(" not in field_type:
        return None
    return class_name(field_type.split("(", 1)[1].rstrip(")"))

# ============================================================
# PARSER
# ============================================================

class DSLParser:
    def __init__(self, text):
        self.lines = [
            line.rstrip()
            for line in text.strip().splitlines()
            if line.strip()
        ]

    def parse(self):
        data = {
            "project": "",
            "module_name": "",
            "model": "",
            "url": "",
            "fields": [],
            "compute": {},
            "header": [],
            "smart": [],
            "list": [],
            "filter": [],
            "form": [],
            "menu": "",
        }

        section = None
        compute_name = None

        for line in self.lines:
            stripped = line.strip()

            if stripped.startswith("project:"):
                data["project"] = stripped.split(":", 1)[1]
                continue
            if stripped.startswith("module:"):
                data["module_name"] = stripped.split(":", 1)[1]
                continue
            if stripped.startswith("url:"):
                data["url"] = stripped.split(":", 1)[1]
                continue
            if not data["model"]:
                data["model"] = stripped
                continue
            if stripped in {
                "compute:", "header:", "smart:",
                "list:", "filter:", "form:", "menu:",
            }:
                section = stripped[:-1]
                compute_name = None
                continue

            if section == "compute":
                if stripped.endswith(":"):
                    compute_name = stripped[:-1]
                    continue
                if compute_name:
                    data["compute"][compute_name] = stripped
                continue

            if section is None and ":" in stripped:
                self.add_field(data, stripped)
                continue

            if section in ("header", "smart", "list", "filter", "form"):
                data[section].append(stripped)
            elif section == "menu":
                data["menu"] = stripped

        return data

    def add_field(self, data, value):
        name, definition = value.split(":", 1)
        required = definition.endswith("*")
        definition = definition.rstrip("*")
        compute = None
        if "=" in definition:
            definition, compute = definition.split("=", 1)

        data["fields"].append({
            "name": name,
            "type": definition,
            "required": required,
            "compute": compute,
        })

# ============================================================
# TEMPLATE GENERATORS
# ============================================================

def generate_model(data, module_name):
    model = class_name(data["model"])
    ns = namespace(data["model"], module_name)
    table = table_name(data["model"])

    fillable = ",\n        ".join(
        f"'{field['name']}'"
        for field in data["fields"]
        if not field["type"].startswith("o2m(")
    )

    appends = ",\n        ".join(
        f"'{field['name']}'"
        for field in data["fields"]
        if field["compute"]
    )

    casts_lines = []
    for field in data["fields"]:
        if field["type"] == "float": casts_lines.append(f"        '{field['name']}' => 'float',")
        elif field["type"] == "bool": casts_lines.append(f"        '{field['name']}' => 'boolean',")
        elif field["type"] == "date": casts_lines.append(f"        '{field['name']}' => 'date',")
        elif field["type"] == "datetime": casts_lines.append(f"        '{field['name']}' => 'datetime',")

    casts_block = ""
    if casts_lines:
        casts_block = "\n    protected $casts = [\n" + "\n".join(casts_lines) + "\n    ];\n"

    relations, accessors = "", ""

    for field in data["fields"]:
        field_type = field["type"]
        if field_type.startswith("m2o("):
            relation_class = relation_model(field_type)
            relations += f"""
    public function {field["name"]}()
    {{
        return $this->belongsTo(\\App\\Modules\\{module_name}\\Model\\{relation_class}::class, '{field["name"]}');
    }}
"""
        elif field_type.startswith("o2m("):
            relation_class = relation_model(field_type)
            foreign_key = table.rstrip("s") + "_id"
            relations += f"""
    public function {field["name"]}()
    {{
        return $this->hasMany(\\App\\Modules\\{module_name}\\Model\\{relation_class}::class, '{foreign_key}');
    }}
"""

    depends_map = {f["compute"]: f["name"] for f in data["fields"] if f["compute"]}
    for compute_name, expr in data["compute"].items():
        target_field = depends_map.get(compute_name, compute_name)
        studly = "".join(p.capitalize() for p in target_field.split("_"))
        body = "        return 0;"
        if expr.strip().startswith("sum(") and expr.strip().endswith(")"):
            inner = expr.strip()[4:-1]
            if "." in inner:
                rel, sub = inner.split(".", 1)
                body = f"        return $this->{rel}->sum('{sub}');"
        accessors += f"""
    public function get{studly}Attribute()
    {{
{body}
    }}
"""

    return f"""<?php

namespace {ns}\\Model;

use Illuminate\\Database\\Eloquent\\Model;

class {model} extends Model
{{
    protected $table = '{table}';

    protected $fillable = [
        {fillable}
    ];{casts_block}
    protected $appends = [
        {appends}
    ];
{relations}{accessors}}}
"""

def migration_column(field):
    name = field["name"]
    field_type = field["type"]
    nullable = "" if field["required"] else "->nullable()"

    if field_type.startswith("m2o("):
        return f"            $table->foreignId('{name}'){nullable};"
    if field_type == "char": return f"            $table->string('{name}'){nullable};"
    if field_type == "text": return f"            $table->text('{name}'){nullable};"
    if field_type == "int": return f"            $table->integer('{name}'){nullable};"
    if field_type == "float": return f"            $table->decimal('{name}', 15, 2){nullable};"
    if field_type == "bool": return f"            $table->boolean('{name}'){nullable};"
    if field_type == "date": return f"            $table->date('{name}'){nullable};"
    if field_type == "datetime": return f"            $table->dateTime('{name}'){nullable};"
    return f"            $table->string('{name}'){nullable};"

def generate_migration(data):
    table = table_name(data["model"])
    columns = [migration_column(f) for f in data["fields"] if not f["type"].startswith("o2m(")]
    columns_text = "\n".join(columns)

    return f"""<?php

use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Database\\Schema\\Blueprint;
use Illuminate\\Support\\Facades\\Schema;

return new class extends Migration {{
    public function up(): void {{
        Schema::create('{table}', function (Blueprint $table) {{$table->id();
{columns_text}
            $table->timestamps();
        }});
    }}

    public function down(): void {{
        Schema::dropIfExists('{table}');
    }}
}};
"""

def generate_repository(data, module_name):
    model = class_name(data["model"])
    ns = namespace(data["model"], module_name)
    filter_fields = data["filter"] or [f["name"] for f in data["fields"]]
    domain_hint = ", ".join(f"'{f}'" for f in filter_fields)

    return f"""<?php

namespace {ns}\\Repository;

use {ns}\\Model\\{model};

class {model}Repository implements {model}RepositoryInterface
{{
    public function __construct(protected {model} $model) {{}}

    public function all(array $domain = [], array $with = []) {{$query = $this->model->newQuery()->with($with);
        foreach ($domain as $field =>$value) {{
            if (in_array($field, [{domain_hint}], true) &&$value !== null && $value !== '') {{$query->where($field,$value);
            }}
        }}
        return $query->latest()->get();
    }}

    public function find($id, array$with = []) {{
        return $this->model->with($with)->findOrFail($id);
    }}

    public function create(array $data) {{
        return $this->model->create($data);
    }}

    public function update($id, array $data) {{$record = $this->find($id);
        $record->update($data);
        return $record;
    }}

    public function delete($id) {{
        return $this->find($id)->delete();
    }}
}}
"""

def generate_repository_interface(data, module_name):
    model = class_name(data["model"])
    ns = namespace(data["model"], module_name)

    return f"""<?php

namespace {ns}\\Repository;

interface {model}RepositoryInterface
{{
    public function all(array $domain = [], array$with = []);
    public function find($id, array$with = []);
    public function create(array $data);
    public function update($id, array$data);
    public function delete($id);
}}
"""

def generate_service(data, module_name):
    model = class_name(data["model"])
    ns = namespace(data["model"], module_name)

    header_methods, smart_methods = "", ""
    for action in data["header"]:
        method = action.strip().replace("-", "_").replace(" ", "_")
        header_methods += f"""
    public function {method}($id) {{$record = $this->repository->find($id);
        // TODO: implement {action.strip()} logic
        return $record;
    }}
"""
    for smart in data["smart"]:
        method = smart.strip().replace("-", "_").replace(" ", "_")
        smart_methods += f"""
    public function {method}Count($id) {{$record = $this->repository->find($id, ['{smart.strip()}']);
        return $record->{smart.strip()}->count();
    }}
"""

    return f"""<?php

namespace {ns}\\Service;

use {ns}\\Repository\\{model}RepositoryInterface;

class {model}Service
{{
    public function __construct(protected {model}RepositoryInterface $repository) {{}}
{header_methods}{smart_methods}
}}
"""

def generate_controller(data, module_name):
    model = class_name(data["model"])
    ns = namespace(data["model"], module_name)
    route_name = data["model"]
    header_actions = ""

    for action in data["header"]:
        method = action.strip().replace("-", "_").replace(" ", "_")
        header_actions += f"""
    public function {method}($id) {{
        $this->service->{method}($id);
        return redirect()->route('{route_name}.show', $id);
    }}
"""

    return f"""<?php

namespace {ns}\\Controller;

use App\\Http\\Controllers\\Controller;
use Illuminate\\Http\\Request;
use Inertia\\Inertia;
use {ns}\\Repository\\{model}RepositoryInterface;
use {ns}\\Service\\{model}Service;
use {ns}\\Request\\{model}Request;

class {model}Controller extends Controller
{{
    public function __construct(
        protected {model}RepositoryInterface $repository,
        protected {model}Service $service
    ) {{}}

    public function index(Request $request) {{
        return Inertia::render('Modules/{module_name}/{model}/Index', [
            'records' => $this->repository->all($request->get('filters', [])),
        ]);
    }}

    public function create() {{
        return Inertia::render('Modules/{module_name}/{model}/Form');
    }}

    public function store({model}Request $request) {{
        $this->repository->create($request->validated());
        return redirect()->route('{route_name}.index');
    }}

    public function show($id) {{
        return Inertia::render('Modules/{module_name}/{model}/Show', [
            'record' => $this->repository->find($id)
        ]);
    }}

    public function edit($id) {{
        return Inertia::render('Modules/{module_name}/{model}/Form', [
            'record' => $this->repository->find($id)
        ]);
    }}

    public function update({model}Request $request, $id) {{$this->repository->update($id,$request->validated());
        return redirect()->route('{route_name}.index');
    }}

    public function destroy($id) {{
        $this->repository->delete($id);
        return redirect()->route('{route_name}.index');
    }}
{header_actions}}}
"""

def generate_request(data, module_name):
    model = class_name(data["model"])
    ns = namespace(data["model"], module_name)
    rules = []

    for field in data["fields"]:
        if field["type"].startswith("o2m(") or field["compute"]: continue
        rule = "required" if field["required"] else "nullable"
        rules.append(f"            '{field['name']}' => '{rule}',")

    return f"""<?php

namespace {ns}\\Request;

use Illuminate\\Foundation\\Http\\FormRequest;

class {model}Request extends FormRequest
{{
    public function authorize(): bool {{ return true; }}

    public function rules(): array {{
        return [
{chr(10).join(rules)}
        ];
    }}
}}
"""

def generate_routes(data, module_name):
    model = class_name(data["model"])
    ns = namespace(data["model"], module_name)
    url = data["url"].strip("/")
    route_name = data["model"]
    extra_routes = ""

    for action in data["header"]:
        method = action.strip().replace("-", "_").replace(" ", "_")
        extra_routes += f"Route::post('{url}/{{id}}/{action.strip()}', [{model}Controller::class, '{method}'])->name('{route_name}.{method}');\n"

    return f"""<?php

use Illuminate\\Support\\Facades\\Route;
use {ns}\\Controller\\{model}Controller;

Route::resource('{url}', {model}Controller::class)->names('{route_name}');
{extra_routes}"""

def generate_list(data):
    model = class_name(data["model"])
    url = data["url"].strip("/")
    headers = "".join(
        f'\n                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">{field}</th>'
        for field in data["list"]
    )
    cells = ""
    for field_name in data["list"]:
        field = next((item for item in data["fields"] if item["name"] == field_name), None)
        value = (
            f"record.{field_name}?.name ?? record.{field_name}"
            if field and field["type"].startswith("m2o(")
            else f"record.{field_name}"
        )
        cells += f'\n                            <td className="px-4 py-3 text-sm text-gray-700">{{{value} ?? "-"}}</td>'

    filters = "".join(
        f"""
                    <label className="block">
                        <span className="mb-1 block text-sm font-medium text-gray-700">{field}</span>
                        <input
                            className="w-full rounded-md border-gray-300 shadow-sm"
                            value={{filters.{field} ?? ""}}
                            onChange={{e => setFilters({{ ...filters, {field}: e.target.value }})}}
                        />
                    </label>"""
        for field in data["filter"]
    )

    return f"""import {{ Link, router }} from "@inertiajs/react";
import {{ useState }} from "react";

export default function Index({{ records = [] }}) {{
    const [filters, setFilters] = useState({{}});
    const applyFilters = () => router.get("/{url}", {{ filters }}, {{ preserveState: true }});

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="mx-auto max-w-7xl">
                <div className="mb-6 flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-semibold text-gray-900">{model}</h1>
                    </div>
                    <Link href="/{url}/create" className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-indigo-700">Create</Link>
                </div>
                <div className="mb-6 rounded-lg bg-white p-4 shadow">
                    <div className="grid gap-4 md:grid-cols-3">{filters}</div>
                    <div className="mt-4 flex gap-2">
                        <button onClick={{applyFilters}} className="rounded-md bg-gray-900 px-4 py-2 text-sm font-semibold text-white">Apply Filters</button>
                        <button onClick={{() => setFilters({{}})}} className="rounded-md border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700">Clear</button>
                    </div>
                </div>
                <div className="overflow-hidden rounded-lg bg-white shadow">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50"><tr>{headers}
                            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-gray-500">Actions</th>
                        </tr></thead>
                        <tbody className="divide-y divide-gray-100">
                            {{records.map(record => (
                                <tr key={{record.id}} className="hover:bg-gray-50">{cells}
                                    <td className="px-4 py-3 text-right">
                                        <Link href={{`/{url}/${{record.id}}`}} className="font-medium text-indigo-600 hover:text-indigo-900">View</Link>
                                    </td>
                                </tr>
                            ))}}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}}
"""

def generate_form(data):
    model = class_name(data["model"])
    url = data["url"].strip("/")
    inputs = ""

    for field in data["fields"]:
        if field["compute"]: continue

        name = field["name"]
        field_type = field["type"]

        if field_type.startswith("m2o("):
            relation = relation_model(field_type)
            inputs += f"""
            <div className="rounded-md border border-gray-200 bg-white p-4">
                <label className="mb-1 block text-sm font-medium text-gray-700">{name}</label>
                <select value={{data.{name} ?? ""}} onChange={{e => setData("{name}", e.target.value)}} className="w-full rounded-md border-gray-300 shadow-sm">
                    <option value="">Select {relation}</option>
                    {{(lookups.{name} ?? []).map(option => <option key={{option.id}} value={{option.id}}>{{option.name ?? option.label ?? option.id}}</option>)}}
                </select>
            </div>"""
        else:
            input_type = {
                "int": "number",
                "float": "number",
                "date": "date",
                "datetime": "datetime-local",
                "bool": "checkbox",
            }.get(field_type, "text")

            if field_type == "text":
                control = f'<textarea value={{data.{name} ?? ""}} onChange={{e => setData("{name}", e.target.value)}} className="w-full rounded-md border-gray-300 shadow-sm" rows="4" />'
            else:
                value_prop = "checked" if input_type == "checkbox" else "value"
                value = f'data.{name} ?? ' + ("false" if input_type == "checkbox" else '""')
                event_value = "e.target.checked" if input_type == "checkbox" else "e.target.value"
                control = f'<input type="{input_type}" {value_prop}={{{value}}} onChange={{e => setData("{name}", {event_value})}} className="w-full rounded-md border-gray-300 shadow-sm" />'

            inputs += f"""
            <div className="rounded-md border border-gray-200 bg-white p-4">
                <label className="mb-1 block text-sm font-medium text-gray-700">{name}</label>
                {control}
            </div>"""

    return f"""import {{ Link, useForm }} from "@inertiajs/react";

export default function Form({{ record, lookups = {{}} }}) {{
    const {{ data, setData, post, put, processing }} = useForm(record ?? {{}});
    const submit = (e) => {{
        e.preventDefault();
        record ? put(`/{url}/${{record.id}}`) : post("/{url}");
    }};

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="mx-auto max-w-5xl">
                <div className="mb-6 flex items-center justify-between">
                    <h1 className="text-2xl font-semibold text-gray-900">{{record ? "Edit" : "Create"}} {model}</h1>
                    <Link href="/{url}" className="text-sm font-medium text-indigo-600 hover:text-indigo-900">Back to list</Link>
                </div>
                <form onSubmit={{submit}} className="space-y-6">
                    <div className="grid gap-4 md:grid-cols-2">{inputs}</div>
                    <div className="flex justify-end gap-3">
                        <Link href="/{url}" className="rounded-md border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700">Cancel</Link>
                        <button type="submit" disabled={{processing}} className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow disabled:opacity-50">{{processing ? "Saving..." : "Save"}}</button>
                    </div>
                </form>
            </div>
        </div>
    );
}}
"""

def generate_show(data):
    model = class_name(data["model"])
    url = data["url"].strip("/")
    header_buttons = "".join(
        f'\n                        <button type="button" onClick={{() => router.post(`/{url}/${{record.id}}/{action.strip()}`)}} className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white">{action.strip().title()}</button>'
        for action in data["header"]
    )
    smart_blocks = "".join(
        f'\n                    <div className="rounded-lg border border-gray-200 bg-white px-4 py-3 shadow-sm"><p className="text-xs uppercase tracking-wide text-gray-500">{smart.strip()}</p><p className="text-xl font-semibold text-gray-900">{{record.{smart.strip()}_count ?? 0}}</p></div>'
        for smart in data["smart"]
    )
    details = "".join(
        f'\n                        <div className="border-b border-gray-100 py-3"><dt className="text-sm font-medium text-gray-500">{field}</dt><dd className="mt-1 text-sm text-gray-900">{{record.{field} ?? "-"}}</dd></div>'
        for field in data["form"]
        if not any(item["name"] == field and item["type"].startswith("o2m(") for item in data["fields"])
    )
    columns = max(1, min(4, len(data["smart"])))

    return f"""import {{ Link, router }} from "@inertiajs/react";

export default function Show({{ record }}) {{
    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="mx-auto max-w-5xl">
                <div className="mb-6 flex items-center justify-between">
                    <h1 className="text-2xl font-semibold text-gray-900">{model}</h1>
                    <div className="flex gap-2">
                        <Link href={{`/{url}/${{record.id}}/edit`}} className="rounded-md border border-gray-300 px-3 py-2 text-sm font-semibold text-gray-700">Edit</Link>{header_buttons}
                    </div>
                </div>
                <div className="mb-6 grid gap-4 md:grid-cols-{columns}">{smart_blocks}</div>
                <div className="rounded-lg bg-white p-6 shadow"><dl className="grid gap-x-8 md:grid-cols-2">{details}</dl></div>
            </div>
        </div>
    );
}}
"""

# ============================================================
# EXECUTOR
# ============================================================

class Generator:
    def __init__(self, data):
        self.data = data
        self.project = Path(data["project"]).expanduser().resolve()
        self.module = data["module_name"] or class_name(data["model"])

    def register_module_routes(self):
        route_path = self.project / "routes" / "web.php"
        route_line = f"require __DIR__.'/../app/Modules/{self.module}/Routes/web.php';"

        if not route_path.exists():
            route_path.parent.mkdir(parents=True, exist_ok=True)
            route_path.write_text("<?php\n", encoding="utf-8")

        content = route_path.read_text(encoding="utf-8")
        if route_line not in content:
            route_path.write_text(content + "\n" + route_line + "\n", encoding="utf-8")
        print(f"✓ Registered routes in routes/web.php: {self.module}")

    def register_repository_binding(self):
        provider_path = self.project / "app" / "Providers" / "AppServiceProvider.php"
        model = class_name(self.data["model"])

        binding = (
            f"        $this->app->bind("
            f"\\App\\Modules\\{self.module}\\Repository\\{model}RepositoryInterface::class, "
            f"\\App\\Modules\\{self.module}\\Repository\\{model}Repository::class);"
        )

        if not provider_path.exists():
            return

        content = provider_path.read_text(encoding="utf-8")
        if binding in content:
            return

        register_marker = "    public function register(): void\n    {\n"
        if register_marker in content:
            content = content.replace(register_marker, register_marker + binding + "\n", 1)
            provider_path.write_text(content, encoding="utf-8")
            print(f"✓ Registered Repository interface binding in AppServiceProvider: {model}")

    def generate(self):
        if not self.project.exists():
            raise FileNotFoundError(f"Project path not found: {self.project}")

        if not (self.project / "artisan").exists():
            raise ValueError("Invalid Laravel project folder. artisan file not found.")

        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        table = table_name(self.data["model"])
        model = class_name(self.data["model"])
        migration_dir = self.project / "database" / "migrations"
        
        existing_migrations = sorted(migration_dir.glob(f"*_create_{table}_table.php"))
        migration_path = existing_migrations[-1] if existing_migrations else migration_dir / f"{timestamp}_create_{table}_table.php"
        migration_relative_path = migration_path.relative_to(self.project)

        files = {
            f"app/Modules/{self.module}/Model/{model}.php": generate_model(self.data, self.module),
            f"app/Modules/{self.module}/Repository/{model}Repository.php": generate_repository(self.data, self.module),
            f"app/Modules/{self.module}/Repository/{model}RepositoryInterface.php": generate_repository_interface(self.data, self.module),
            f"app/Modules/{self.module}/Service/{model}Service.php": generate_service(self.data, self.module),
            f"app/Modules/{self.module}/Controller/{model}Controller.php": generate_controller(self.data, self.module),
            f"app/Modules/{self.module}/Request/{model}Request.php": generate_request(self.data, self.module),
            str(migration_relative_path): generate_migration(self.data),
            f"app/Modules/{self.module}/Routes/web.php": generate_routes(self.data, self.module),
            f"resources/js/Pages/Modules/{self.module}/{model}/Index.jsx": generate_list(self.data),
            f"resources/js/Pages/Modules/{self.module}/{model}/Form.jsx": generate_form(self.data),
            f"resources/js/Pages/Modules/{self.module}/{model}/Show.jsx": generate_show(self.data),
        }

        for relative_path, content in files.items():
            file_path = self.project / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            print(f"✓ Created: {relative_path}")

        self.register_module_routes()
        self.register_repository_binding()

        print(f"\n✓ Module generation complete: {self.module}")
        print("Next steps:")
        print(f"  cd {self.project}")
        print("  php artisan migrate")

if __name__ == "__main__":
    parser = DSLParser(DSL)
    data = parser.parse()
    Generator(data).generate()
