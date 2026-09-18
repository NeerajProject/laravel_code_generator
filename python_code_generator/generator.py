from pathlib import Path
from datetime import datetime

# ============================================================
# DSL (Grammar for Odoo-like modular Laravel generator)
# ============================================================

DSL = """

project:/home/nj/workspace/laravel_code_generator/laravel_code_generator/laraval_caste/my_laravel_app
module:Sale

sale.order
url:/sale-orders

name:char*
customer_id:m2o(res.partner)
order_date:date
state:selection(draft,confirmed,cancelled)
amount_total:float=compute_total
note:text
order_line_ids:o2m(sale.order.line)

list:
    name
    customer_id
    order_date
    state
    amount_total

filter:
    name
    customer_id
    order_date
    state

form:
    name
    customer_id
    order_date
    state
    order_line_ids
    note
    amount_total

compute:
    compute_total:
        sum(order_line_ids.subtotal)

menu:
    Sale/Sale Orders


sale.order.line
url:/sale-order-lines

order_id:m2o(sale.order)
product_id:m2o(product.product)
quantity:float
unit_price:float
subtotal:float=compute_subtotal

list:
    product_id
    quantity
    unit_price
    subtotal

filter:
    product_id
    order_id

form:
    product_id
    quantity
    unit_price
    subtotal

compute:
    compute_subtotal:
        quantity * unit_price
"""

# ============================================================
# HELPERS
# ============================================================

def class_name(model):
    """sale.order -> SaleOrder, project.project -> ProjectProject"""
    return "".join(part.capitalize() for part in model.split("."))

def table_name(model):
    """sale.order -> sale_orders, project.project -> project_projects"""
    return model.replace(".", "_") + "s"

def namespace(model, module_name=None):
    """sale.order -> App\\Modules\\Product"""
    return f"App\\Modules\\{module_name or class_name(model)}"

def relation_model(field_type):
    """m2o(res.partner) -> ResPartner, o2m(project.task) -> ProjectTask"""
    if "(" not in field_type:
        return None
    inner = field_type.split("(", 1)[1].rstrip(")")
    raw_model = inner.split(",", 1)[0].strip()
    return class_name(raw_model)

def relation_raw_model(field_type):
    """o2m(project.task) -> project.task"""
    if "(" not in field_type:
        return None
    inner = field_type.split("(", 1)[1].rstrip(")")
    return inner.split(",", 1)[0].strip()

def human_label(name):
    """task_ids -> Tasks, is_active -> Active, name -> Name"""
    clean = name.replace("_ids", "").replace("_id", "").replace("_", " ")
    return " ".join(word.capitalize() for word in clean.split())

def relation_columns(field_type, model_raw=None):
    """Returns list of column dicts for an o2m relation widget."""
    raw = model_raw or relation_raw_model(field_type) or ""
    if "task" in raw.lower():
        return [
            {"name": "name", "label": "Task Title", "type": "text", "placeholder": "e.g. Design homepage"},
            {"name": "description", "label": "Description", "type": "text", "placeholder": "Details..."},
            {"name": "is_done", "label": "Done", "type": "bool"},
        ]
    elif "line" in raw.lower():
        return [
            {"name": "name", "label": "Description", "type": "text", "placeholder": "Item description"},
            {"name": "quantity", "label": "Quantity", "type": "number", "defaultValue": 1},
            {"name": "price_unit", "label": "Unit Price", "type": "number", "defaultValue": 0.0},
            {"name": "subtotal", "label": "Subtotal", "type": "number", "defaultValue": 0.0},
        ]
    else:
        return [
            {"name": "name", "label": "Name", "type": "text", "placeholder": "Title / Name"},
            {"name": "description", "label": "Description", "type": "text", "placeholder": "Details..."},
            {"name": "is_done", "label": "Done", "type": "bool"},
        ]

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

def generate_child_model(child_raw, parent_data, module_name):
    child_class = class_name(child_raw)
    child_table = table_name(child_raw)
    parent_table = table_name(parent_data["model"])
    parent_class = class_name(parent_data["model"])
    foreign_key = parent_table.rstrip("s") + "_id"
    ns = namespace(child_raw, module_name)

    return f"""<?php

namespace {ns}\\Model;

use Illuminate\\Database\\Eloquent\\Model;

class {child_class} extends Model
{{
    protected $table = '{child_table}';

    protected $fillable = [
        '{foreign_key}',
        'name',
        'description',
        'is_done',
    ];

    protected $casts = [
        'is_done' => 'boolean',
    ];

    public function project()
    {{
        return $this->belongsTo({parent_class}::class, '{foreign_key}');
    }}
}}
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
        if (!Schema::hasTable('{table}')) {{
            Schema::create('{table}', function (Blueprint $table) {{
                $table->id();
{columns_text}
                $table->timestamps();
            }});
        }}
    }}

    public function down(): void {{
        Schema::dropIfExists('{table}');
    }}
}};
"""

def generate_child_migration(child_raw, parent_data):
    child_table = table_name(child_raw)
    parent_table = table_name(parent_data["model"])
    foreign_key = parent_table.rstrip("s") + "_id"

    return f"""<?php

use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Database\\Schema\\Blueprint;
use Illuminate\\Support\\Facades\\Schema;

return new class extends Migration {{
    public function up(): void {{
        if (!Schema::hasTable('{child_table}')) {{
            Schema::create('{child_table}', function (Blueprint $table) {{
                $table->id();
                $table->foreignId('{foreign_key}')->nullable()->constrained('{parent_table}')->cascadeOnDelete();
                $table->string('name')->nullable();
                $table->text('description')->nullable();
                $table->boolean('is_done')->default(false);
                $table->timestamps();
            }});
        }}
    }}

    public function down(): void {{
        Schema::dropIfExists('{child_table}');
    }}
}};
"""

def generate_repository(data, module_name):
    model = class_name(data["model"])
    ns = namespace(data["model"], module_name)
    filter_fields = data["filter"] or [f["name"] for f in data["fields"] if not f["type"].startswith("o2m(")]
    domain_hint = ", ".join(f"'{f}'" for f in filter_fields)

    o2m_fields = [f for f in data["fields"] if f["type"].startswith("o2m(")]
    m2o_fields = [f for f in data["fields"] if f["type"].startswith("m2o(")]
    all_relations = [f["name"] for f in o2m_fields] + [f["name"] for f in m2o_fields]
    relations_php = ", ".join(f"'{r}'" for r in all_relations)

    # Building o2m extraction and saving blocks
    o2m_extract_create = "\n".join(
        f"        if (isset($data['{f['name']}'])) {{\n"
        f"            $o2mData['{f['name']}'] = $data['{f['name']}'];\n"
        f"            unset($data['{f['name']}']);\n"
        f"        }}"
        for f in o2m_fields
    )

    o2m_save_create = "\n".join(
        f"        if (isset($o2mData['{f['name']}']) && is_array($o2mData['{f['name']}'])) {{\n"
        f"            foreach ($o2mData['{f['name']}'] as $line) {{\n"
        f"                if (is_array($line)) {{\n"
        f"                    unset($line['id']);\n"
        f"                    if (!empty(array_filter($line, fn($v) => $v !== null && $v !== '' && $v !== false))) {{\n"
        f"                        $record->{f['name']}()->create($line);\n"
        f"                    }}\n"
        f"                }}\n"
        f"            }}\n"
        f"        }}"
        for f in o2m_fields
    )

    o2m_extract_update = o2m_extract_create

    o2m_save_update = "\n".join(
        f"        if (isset($o2mData['{f['name']}']) && is_array($o2mData['{f['name']}'])) {{\n"
        f"            $keptIds = [];\n"
        f"            foreach ($o2mData['{f['name']}'] as $line) {{\n"
        f"                if (!is_array($line)) continue;\n"
        f"                $lineId = $line['id'] ?? null;\n"
        f"                unset($line['id']);\n"
        f"                if (empty(array_filter($line, fn($v) => $v !== null && $v !== '' && $v !== false))) {{\n"
        f"                    continue;\n"
        f"                }}\n"
        f"                if ($lineId) {{\n"
        f"                    $record->{f['name']}()->where('id', $lineId)->update($line);\n"
        f"                    $keptIds[] = $lineId;\n"
        f"                }} else {{\n"
        f"                    $created = $record->{f['name']}()->create($line);\n"
        f"                    $keptIds[] = $created->id;\n"
        f"                }}\n"
        f"            }}\n"
        f"            $record->{f['name']}()->whereNotIn('id', $keptIds)->delete();\n"
        f"        }}"
        for f in o2m_fields
    )

    # Build search conditions for text filters
    text_filter_cols = [
        f["name"] for f in data["fields"]
        if f["name"] in filter_fields and f["type"] in ("char", "text")
    ]
    if not text_filter_cols and filter_fields:
        text_filter_cols = [filter_fields[0]]

    search_conditions = ""
    for idx, col in enumerate(text_filter_cols):
        method = "where" if idx == 0 else "orWhere"
        search_conditions += f"                $q->{method}('{col}', 'like', \"%{{$search}}%\");\n"

    return f"""<?php

namespace {ns}\\Repository;

use {ns}\\Model\\{model};

class {model}Repository implements {model}RepositoryInterface
{{
    public function __construct(protected {model} $model) {{}}

    public function all(array $domain = [], array $with = [])
    {{
        $defaultWith = [{relations_php}];
        $eager = array_unique(array_merge($defaultWith, $with));
        $query = $this->model->newQuery()->with($eager);

        // General search across filterable fields (Odoo unified search)
        $search = $domain['search'] ?? $domain['query'] ?? null;
        if (!empty($search)) {{$query->where(function($q) use ($search) {{
{search_conditions}            }});
        }}

        // Specific field filters (Odoo facet filter chips)
        foreach ($domain as $field => $value) {{
            if (in_array($field, ['search', 'query', 'sort_field', 'sort_direction'], true) || $value === null || $value === '') {{
                continue;
            }}

            if (in_array($field, [{domain_hint}], true)) {{
                if (is_bool($value) || $value === 'true' || $value === 'false') {{
                    $boolVal = filter_var($value, FILTER_VALIDATE_BOOLEAN);
                    $query->where($field, $boolVal);
                }} else {{
                    $query->where($field, 'like', "%{{$value}}%");
                }}
            }}
        }}

        $sortField = $domain['sort_field'] ?? 'id';
        $sortDirection = $domain['sort_direction'] ?? 'desc';
        if (in_array($sortField, ['id', {domain_hint}], true)) {{
            $query->orderBy($sortField, strtolower($sortDirection) === 'asc' ? 'asc' : 'desc');
        }} else {{
            $query->latest();
        }}

        return $query->get();
    }}

    public function find($id, array $with = [])
    {{
        $defaultWith = [{relations_php}];
        $eager = array_unique(array_merge($defaultWith, $with));
        return $this->model->with($eager)->findOrFail($id);
    }}

    public function create(array $data)
    {{
        $o2mData = [];
{o2m_extract_create}

        $record = $this->model->create($data);

{o2m_save_create}

        return $record->load([{relations_php}]);
    }}

    public function update($id, array $data)
    {{
        $record = $this->find($id);
        $o2mData = [];
{o2m_extract_update}

        $record->update($data);

{o2m_save_update}

        return $record->load([{relations_php}]);
    }}

    public function delete($id)
    {{
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
    public function all(array $domain = [], array $with = []);
    public function find($id, array $with = []);
    public function create(array $data);
    public function update($id, array $data);
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
    public function {method}($id)
    {{
        $record = $this->repository->find($id);
        // TODO: implement {action.strip()} logic
        return $record;
    }}
"""
    for smart in data["smart"]:
        method = smart.strip().replace("-", "_").replace(" ", "_")
        smart_methods += f"""
    public function {method}Count($id)
    {{
        $record = $this->repository->find($id, ['{smart.strip()}']);
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
    public function {method}($id)
    {{
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

    public function index(Request $request)
    {{
        $filters = $request->get('filters', []);
        if ($request->has('search') && !isset($filters['search'])) {{
            $filters['search'] = $request->get('search');
        }}

        return Inertia::render('Modules/{module_name}/{model}/Index', [
            'records' => $this->repository->all($filters),
            'filters' => $filters,
        ]);
    }}

    public function create()
    {{
        return Inertia::render('Modules/{module_name}/{model}/Form', [
            'record' => null,
            'lookups' => [],
        ]);
    }}

    public function store({model}Request $request)
    {{
        $this->repository->create($request->validated());
        return redirect()->route('{route_name}.index');
    }}

    public function show($id)
    {{
        return Inertia::render('Modules/{module_name}/{model}/Show', [
            'record' => $this->repository->find($id),
        ]);
    }}

    public function edit($id)
    {{
        return Inertia::render('Modules/{module_name}/{model}/Form', [
            'record' => $this->repository->find($id),
            'lookups' => [],
        ]);
    }}

    public function update({model}Request $request, $id)
    {{
        $this->repository->update($id, $request->validated());
        return redirect()->route('{route_name}.index');
    }}

    public function destroy($id)
    {{
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
        if field["compute"]: continue

        if field["type"].startswith("o2m("):
            col_list = relation_columns(field["type"])
            rules.append(f"            '{field['name']}' => 'nullable|array',")
            for col in col_list:
                ctype = "numeric" if col["type"] == "number" else ("boolean" if col["type"] == "bool" else "string|max:255")
                rules.append(f"            '{field['name']}.*.{col['name']}' => 'nullable|{ctype}',")
            continue

        rule = "required" if field["required"] else "nullable"
        if field["type"] == "bool":
            rules.append(f"            '{field['name']}' => 'nullable|boolean',")
        elif field["type"] in ("int", "float"):
            rules.append(f"            '{field['name']}' => '{rule}|numeric',")
        elif field["type"] == "text":
            rules.append(f"            '{field['name']}' => '{rule}|string',")
        else:
            rules.append(f"            '{field['name']}' => '{rule}|string|max:255',")

    return f"""<?php

namespace {ns}\\Request;

use Illuminate\\Foundation\\Http\\FormRequest;

class {model}Request extends FormRequest
{{
    public function authorize(): bool {{ return true; }}

    public function rules(): array
    {{
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

def generate_one2many_component():
    return """import React from "react";

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
"""

def generate_list(data):
    model = class_name(data["model"])
    url = data["url"].strip("/")

    menu_parts = (data["menu"] or f"{model}/{model}").split("/")
    app_name = menu_parts[0].strip()
    menu_name = menu_parts[1].strip() if len(menu_parts) > 1 else app_name

    headers = "".join(
        f'\n                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">{human_label(field)}</th>'
        for field in data["list"]
    )

    cells = ""
    for field_name in data["list"]:
        field = next((item for item in data["fields"] if item["name"] == field_name), None)
        ftype = field["type"] if field else ""

        if ftype == "bool":
            cell_expr = (
                f'{{record.{field_name} ? (\n'
                f'                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">Active</span>\n'
                f'                            ) : (\n'
                f'                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">Inactive</span>\n'
                f'                            )}}'
            )
        elif ftype.startswith("m2o("):
            cell_expr = f'{{record.{field_name}?.name ?? record.{field_name} ?? "-"}}'
        elif ftype.startswith("o2m("):
            cell_expr = (
                f'<span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-purple-50 text-[#714B67] border border-purple-200">\n'
                f'                                {{record.{field_name}?.length ?? 0}} lines\n'
                f'                            </span>'
            )
        elif field_name == "name":
            cell_expr = f'<Link href={{`/{url}/${{record.id}}`}} className="font-semibold text-gray-900 hover:text-[#714B67] transition">{{record.{field_name} || "-"}}</Link>'
        else:
            cell_expr = f'{{record.{field_name} ?? "-"}}'

        cells += f'\n                            <td className="px-4 py-3 text-sm text-gray-700">{cell_expr}</td>'

    has_active_field = any(f["name"] == "is_active" for f in data["fields"])
    filter_fields = [f for f in data["filter"] if f != "is_active"]

    quick_inputs = ""
    for ff in filter_fields:
        flabel = human_label(ff)
        quick_inputs += f"""
                        <div className="py-1">
                            <label className="block text-[11px] font-medium text-gray-600 mb-0.5">{flabel}</label>
                            <input
                                type="text"
                                value={{filtersState.{ff} ?? ""}}
                                onChange={{(e) => updateSpecificFilter("{ff}", e.target.value)}}
                                placeholder="Filter by {flabel}..."
                                className="w-full text-xs rounded border-gray-300 py-1 px-2 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67]"
                            />
                        </div>"""

    active_toggle_jsx = ""
    if has_active_field:
        active_toggle_jsx = """
                        <label className="flex items-center gap-2 py-1.5 text-gray-700 hover:bg-gray-50 px-1 rounded cursor-pointer select-none">
                            <input
                                type="checkbox"
                                checked={filtersState.is_active === "true" || filtersState.is_active === true}
                                onChange={toggleActiveFilter}
                                className="rounded border-gray-300 text-[#714B67] focus:ring-[#714B67]"
                            />
                            <span className="font-medium">Active records only</span>
                        </label>"""

    col_count = len(data["list"]) + 2

    return f"""import {{ Link, router }} from "@inertiajs/react";
import {{ useState }} from "react";

export default function Index({{ records = [], filters = {{}} }}) {{
    const [filtersState, setFiltersState] = useState(filters ?? {{}});
    const [searchInput, setSearchInput] = useState(filters?.search ?? "");
    const [showFilterMenu, setShowFilterMenu] = useState(false);
    const [selectedIds, setSelectedIds] = useState([]);

    const applyFilters = (newFilters) => {{
        const cleaned = {{}};
        for (const [k, v] of Object.entries(newFilters)) {{
            if (v !== undefined && v !== null && v !== "") {{
                cleaned[k] = v;
            }}
        }}
        router.get("/{url}", {{ filters: cleaned }}, {{ preserveState: true, replace: true }});
    }};

    const handleSearchSubmit = (e) => {{
        if (e) e.preventDefault();
        const updated = {{ ...filtersState, search: searchInput.trim() }};
        setFiltersState(updated);
        applyFilters(updated);
    }};

    const removeFilter = (key) => {{
        const updated = {{ ...filtersState }};
        delete updated[key];
        if (key === "search") setSearchInput("");
        setFiltersState(updated);
        applyFilters(updated);
    }};

    const updateSpecificFilter = (key, value) => {{
        const updated = {{ ...filtersState, [key]: value }};
        setFiltersState(updated);
        applyFilters(updated);
    }};

    const toggleActiveFilter = () => {{
        const current = filtersState.is_active;
        const next = current === "true" || current === true ? "" : "true";
        updateSpecificFilter("is_active", next);
    }};

    const clearAllFilters = () => {{
        setSearchInput("");
        setFiltersState({{}});
        applyFilters({{}});
        setShowFilterMenu(false);
    }};

    const applySort = (field, direction) => {{
        const updated = {{ ...filtersState, sort_field: field, sort_direction: direction }};
        setFiltersState(updated);
        applyFilters(updated);
        setShowFilterMenu(false);
    }};

    const toggleSelectAll = () => {{
        if (records.length > 0 && selectedIds.length === records.length) {{
            setSelectedIds([]);
        }} else {{
            setSelectedIds(records.map((r) => r.id));
        }}
    }};

    const toggleSelectRow = (id) => {{
        setSelectedIds((prev) =>
            prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
        );
    }};

    const activeFilterEntries = Object.entries(filtersState).filter(
        ([k, v]) => k !== "search" && !k.startsWith("sort_") && v !== "" && v !== undefined && v !== null
    );
    const hasActiveFilters = Boolean(searchInput || filtersState.search || activeFilterEntries.length > 0);

    return (
        <div className="min-h-screen bg-[#f8fafc]">
            {{/* Odoo Top Navigation Bar */}}
            <nav className="bg-[#714B67] text-white px-6 py-2.5 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
                        <span className="text-xl">⠿</span>
                        <span>{app_name}</span>
                    </div>
                    <div className="flex items-center gap-4 text-sm font-medium text-purple-100">
                        <Link href="/{url}" className="hover:text-white transition">{menu_name}</Link>
                    </div>
                </div>
                <div className="flex items-center gap-3 text-xs text-purple-200">
                    <span className="w-7 h-7 rounded-full bg-purple-900/60 border border-purple-400/40 flex items-center justify-center font-bold text-white text-xs">
                        NJ
                    </span>
                </div>
            </nav>

            {{/* Odoo Control Panel */}}
            <div className="bg-white border-b border-gray-200 px-6 py-3 shadow-2xs">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    {{/* Left: Breadcrumbs & Action Buttons */}}
                    <div className="flex items-center gap-4">
                        <h1 className="text-xl font-bold text-gray-900">{model}</h1>
                        <Link
                            href="/{url}/create"
                            className="inline-flex items-center gap-1.5 rounded bg-[#714B67] hover:bg-[#5a3b52] px-3.5 py-1.5 text-sm font-semibold text-white shadow-sm transition"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                            </svg>
                            New
                        </Link>
                        {{selectedIds.length > 0 && (
                            <div className="flex items-center gap-2 pl-3 border-l border-gray-200 text-xs">
                                <span className="font-medium text-gray-600">{{selectedIds.length}} selected</span>
                            </div>
                        )}}
                    </div>

                    {{/* Right: Odoo Search Bar, Filters Dropdown, Pager */}}
                    <div className="flex items-center gap-3 relative">
                        {{/* Search Input Box */}}
                        <form
                            onSubmit={{handleSearchSubmit}}
                            className="relative flex items-center bg-white border border-gray-300 rounded shadow-sm px-2.5 py-1 text-sm min-w-[280px] sm:min-w-[360px] focus-within:ring-2 focus-within:ring-[#714B67] focus-within:border-transparent"
                        >
                            <svg className="w-4 h-4 text-gray-400 mr-1.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>

                            {{/* Filter Chips inside search bar */}}
                            <div className="flex flex-wrap gap-1 items-center flex-1">
                                {{filtersState.search && (
                                    <span className="inline-flex items-center gap-1 bg-purple-100 text-[#714B67] text-xs px-2 py-0.5 rounded font-medium">
                                        Search: &quot;{{filtersState.search}}&quot;
                                        <button type="button" onClick={{() => removeFilter("search")}} className="hover:text-purple-900">×</button>
                                    </span>
                                )}}
                                {{activeFilterEntries.map(([key, val]) => (
                                    <span key={{key}} className="inline-flex items-center gap-1 bg-purple-50 border border-purple-200 text-[#714B67] text-xs px-2 py-0.5 rounded font-medium">
                                        {{key}}: {{String(val)}}
                                        <button type="button" onClick={{() => removeFilter(key)}} className="hover:text-purple-900">×</button>
                                    </span>
                                ))}}
                                <input
                                    type="text"
                                    value={{searchInput}}
                                    onChange={{(e) => setSearchInput(e.target.value)}}
                                    placeholder="Search..."
                                    className="border-0 focus:ring-0 text-sm py-0.5 px-1.5 flex-1 min-w-[80px] outline-none text-gray-800 placeholder-gray-400"
                                />
                            </div>

                            {{hasActiveFilters && (
                                <button
                                    type="button"
                                    onClick={{clearAllFilters}}
                                    className="text-gray-400 hover:text-gray-600 p-0.5 mx-1"
                                    title="Clear all filters"
                                >
                                    ×
                                </button>
                            )}}

                            {{/* Filters Dropdown Trigger Button */}}
                            <button
                                type="button"
                                onClick={{() => setShowFilterMenu(!showFilterMenu)}}
                                className="ml-1 p-1 text-gray-500 hover:text-[#714B67] rounded hover:bg-gray-100 flex items-center gap-1 text-xs font-semibold"
                            >
                                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                                </svg>
                                Filters
                                <span className="text-[10px]">▼</span>
                            </button>
                        </form>

                        {{/* Odoo Filter Menu Popover */}}
                        {{showFilterMenu && (
                            <div className="absolute right-0 top-full mt-2 w-72 bg-white border border-gray-200 rounded-md shadow-xl p-3 z-30 divide-y divide-gray-100 text-xs">
                                <div className="pb-2">
                                    <p className="font-bold text-gray-500 uppercase tracking-wider text-[10px] mb-1.5 flex items-center gap-1">
                                        <span>🔍</span> Quick Filters
                                    </p>
                                    {active_toggle_jsx}
                                    {quick_inputs}
                                </div>
                                <div className="py-2">
                                    <p className="font-bold text-gray-500 uppercase tracking-wider text-[10px] mb-1.5 flex items-center gap-1">
                                        <span>⇅</span> Sort
                                    </p>
                                    <div className="flex flex-col gap-1">
                                        <button type="button" onClick={{() => applySort("name", "asc")}} className="text-left px-1.5 py-1 rounded text-gray-700 hover:bg-gray-100 font-medium">Name (A → Z)</button>
                                        <button type="button" onClick={{() => applySort("name", "desc")}} className="text-left px-1.5 py-1 rounded text-gray-700 hover:bg-gray-100 font-medium">Name (Z → A)</button>
                                        <button type="button" onClick={{() => applySort("id", "desc")}} className="text-left px-1.5 py-1 rounded text-gray-700 hover:bg-gray-100 font-medium">Newest First</button>
                                    </div>
                                </div>
                                {{hasActiveFilters && (
                                    <div className="pt-2">
                                        <button
                                            type="button"
                                            onClick={{clearAllFilters}}
                                            className="w-full text-left px-1.5 py-1 rounded text-red-600 hover:bg-red-50 font-semibold"
                                        >
                                            Clear All Filters
                                        </button>
                                    </div>
                                )}}
                            </div>
                        )}}

                        {{/* Pager */}}
                        <div className="text-xs text-gray-500 font-medium whitespace-nowrap hidden sm:block">
                            {{records.length > 0 ? `1-${{records.length}}` : 0}} / {{records.length}}
                        </div>
                    </div>
                </div>
            </div>

            {{/* Odoo List Table */}}
            <div className="max-w-7xl mx-auto px-6 py-6">
                <div className="bg-white border border-gray-200 rounded shadow-2xs overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200 text-sm">
                        <thead className="bg-gray-50/80">
                            <tr>
                                <th className="w-10 px-4 py-3 text-left">
                                    <input
                                        type="checkbox"
                                        checked={{records.length > 0 && selectedIds.length === records.length}}
                                        onChange={{toggleSelectAll}}
                                        className="rounded border-gray-300 text-[#714B67] focus:ring-[#714B67]"
                                    />
                                </th>{headers}
                                <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 bg-white">
                            {{records.length > 0 ? (
                                records.map((record) => (
                                    <tr key={{record.id}} className="hover:bg-purple-50/30 transition">
                                        <td className="px-4 py-3">
                                            <input
                                                type="checkbox"
                                                checked={{selectedIds.includes(record.id)}}
                                                onChange={{() => toggleSelectRow(record.id)}}
                                                className="rounded border-gray-300 text-[#714B67] focus:ring-[#714B67]"
                                            />
                                        </td>{cells}
                                        <td className="px-4 py-3 text-right whitespace-nowrap">
                                            <Link href={{`/{url}/${{record.id}}`}} className="text-xs font-semibold text-[#714B67] hover:underline mr-3">View</Link>
                                            <Link href={{`/{url}/${{record.id}}/edit`}} className="text-xs font-medium text-gray-600 hover:text-gray-900">Edit</Link>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={{{col_count}}} className="px-4 py-16 text-center text-gray-500">
                                        <div className="flex flex-col items-center justify-center">
                                            <svg className="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                            </svg>
                                            <p className="text-base font-semibold text-gray-700">No {model} records found</p>
                                            <p className="text-xs text-gray-400 mt-1">Try adjusting your search or filters, or create a new record.</p>
                                            <Link
                                                href="/{url}/create"
                                                className="mt-4 rounded bg-[#714B67] hover:bg-[#5a3b52] px-4 py-1.5 text-xs font-semibold text-white shadow-sm transition"
                                            >
                                                + Create {model}
                                            </Link>
                                        </div>
                                    </td>
                                </tr>
                            )}}
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

    menu_parts = (data["menu"] or f"{model}/{model}").split("/")
    app_name = menu_parts[0].strip()
    menu_name = menu_parts[1].strip() if len(menu_parts) > 1 else app_name

    o2m_fields = [f for f in data["fields"] if f["type"].startswith("o2m(")]
    has_description = any(f["name"] == "description" for f in data["fields"])

    default_tab = o2m_fields[0]["name"] if o2m_fields else ("description" if has_description else "")

    # Identify the primary title field (usually name)
    title_field = next((f for f in data["fields"] if f["name"] == "name"), None)
    if not title_field:
        title_field = next((f for f in data["fields"] if f["type"] == "char"), None)
    title_name = title_field["name"] if title_field else "name"

    # Default values for useForm
    default_props = []
    for f in data["fields"]:
        if f["type"].startswith("o2m("):
            default_props.append(f"        {f['name']}: record?.{f['name']} ?? [],")
        elif f["type"] == "bool":
            default_props.append(f"        {f['name']}: record?.{f['name']} ?? false,")
    defaults_block = "\n" + "\n".join(default_props) if default_props else ""

    # Smart buttons in Form view
    smart_buttons = ""
    for o2m in o2m_fields:
        olabel = human_label(o2m["name"])
        smart_buttons += f"""
                    <button
                        type="button"
                        onClick={{() => setActiveTab("{o2m['name']}")}}
                        className="flex flex-col items-center justify-center border border-gray-200 rounded px-4 py-1.5 bg-gray-50/70 hover:bg-purple-50 hover:border-purple-200 transition text-right shadow-2xs cursor-pointer"
                    >
                        <span className="text-xl font-bold text-gray-900 leading-tight">
                            {{data.{o2m['name']}?.length || 0}}
                        </span>
                        <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
                            {olabel}
                        </span>
                    </button>"""

    # Scalar fields (excluding title_name, description, and o2m)
    scalar_fields = ""
    for field in data["fields"]:
        fname = field["name"]
        ftype = field["type"]
        if fname in (title_name, "description") or ftype.startswith("o2m(") or field["compute"]:
            continue

        flabel = human_label(fname)

        if ftype.startswith("m2o("):
            rel_class = relation_model(ftype)
            scalar_fields += f"""
                <div className="space-y-1">
                    <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600">{flabel}</label>
                    <select
                        value={{data.{fname} ?? ""}}
                        onChange={{(e) => setData("{fname}", e.target.value)}}
                        className="w-full text-sm rounded border-gray-300 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm py-1.5 px-3"
                    >
                        <option value="">Select {rel_class}</option>
                        {{(lookups.{fname} ?? []).map((opt) => (
                            <option key={{opt.id}} value={{opt.id}}>{{opt.name ?? opt.label ?? opt.id}}</option>
                        ))}}
                    </select>
                    {{errors.{fname} && <p className="text-xs text-red-600">{{errors.{fname}}}</p>}}
                </div>"""
        elif ftype == "bool":
            scalar_fields += f"""
                <div className="flex items-center gap-3 pt-5">
                    <input
                        type="checkbox"
                        id="{fname}"
                        checked={{Boolean(data.{fname})}}
                        onChange={{(e) => setData("{fname}", e.target.checked)}}
                        className="rounded border-gray-300 text-[#714B67] focus:ring-[#714B67] w-4 h-4 cursor-pointer"
                    />
                    <label htmlFor="{fname}" className="text-sm font-semibold text-gray-700 cursor-pointer select-none">
                        {flabel}
                    </label>
                    {{errors.{fname} && <p className="text-xs text-red-600">{{errors.{fname}}}</p>}}
                </div>"""
        else:
            itype = "number" if ftype in ("int", "float") else ("date" if ftype == "date" else ("datetime-local" if ftype == "datetime" else "text"))
            scalar_fields += f"""
                <div className="space-y-1">
                    <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600">{flabel}</label>
                    <input
                        type="{itype}"
                        value={{data.{fname} ?? ""}}
                        onChange={{(e) => setData("{fname}", e.target.value)}}
                        placeholder="{flabel}..."
                        className="w-full text-sm rounded border-gray-300 focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm py-1.5 px-3"
                    />
                    {{errors.{fname} && <p className="text-xs text-red-600">{{errors.{fname}}}</p>}}
                </div>"""

    # Notebook tabs navigation and content
    tab_headers = ""
    tab_contents = ""

    for o2m in o2m_fields:
        olabel = human_label(o2m["name"])
        cols = relation_columns(o2m["type"])
        cols_js = str(cols).replace("'", '"')

        tab_headers += f"""
                        <button
                            type="button"
                            onClick={{() => setActiveTab("{o2m['name']}")}}
                            className={{`pb-2.5 px-3 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${{
                                activeTab === "{o2m['name']}"
                                    ? "border-[#714B67] text-[#714B67]"
                                    : "border-transparent text-gray-500 hover:text-gray-700"
                            }}`}}
                        >
                            <span>{olabel}</span>
                            <span className="px-1.5 py-0.5 rounded-full text-xs font-bold bg-purple-100 text-[#714B67]">
                                {{data.{o2m['name']}?.length || 0}}
                            </span>
                        </button>"""

        tab_contents += f"""
                    {{activeTab === "{o2m['name']}" && (
                        <One2ManyField
                            name="{o2m['name']}"
                            label="{olabel}"
                            value={{data.{o2m['name']} || []}}
                            onChange={{(lines) => setData("{o2m['name']}", lines)}}
                            columns={{{cols_js}}}
                            error={{errors.{o2m['name']}}}
                        />
                    )}}"""

    if has_description:
        tab_headers += f"""
                        <button
                            type="button"
                            onClick={{() => setActiveTab("description")}}
                            className={{`pb-2.5 px-3 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${{
                                activeTab === "description"
                                    ? "border-[#714B67] text-[#714B67]"
                                    : "border-transparent text-gray-500 hover:text-gray-700"
                            }}`}}
                        >
                            Description
                        </button>"""

        tab_contents += f"""
                    {{activeTab === "description" && (
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">Description / Notes</label>
                            <textarea
                                value={{data.description ?? ""}}
                                onChange={{(e) => setData("description", e.target.value)}}
                                rows={{6}}
                                className="w-full rounded border-gray-300 text-sm focus:border-[#714B67] focus:ring-1 focus:ring-[#714B67] shadow-sm p-3"
                                placeholder="Add detailed notes or description..."
                            />
                            {{errors.description && <p className="text-xs text-red-600 mt-1">{{errors.description}}</p>}}
                        </div>
                    )}}"""

    notebook_jsx = ""
    if o2m_fields or has_description:
        notebook_jsx = f"""
                {{/* Notebook / Tabs */}}
                <div className="mt-8 border-t border-gray-100 pt-6">
                    <div className="flex border-b border-gray-200 space-x-6">
                        {tab_headers}
                    </div>
                    <div className="pt-4">
                        {tab_contents}
                    </div>
                </div>"""

    return f"""import {{ Link, useForm }} from "@inertiajs/react";
import {{ useState }} from "react";
import One2ManyField from "@/Components/Generated/One2ManyField";

export default function Form({{ record, lookups = {{}} }}) {{
    const {{ data, setData, post, put, processing, errors }} = useForm({{
        ...record,{defaults_block}
    }});

    const [activeTab, setActiveTab] = useState("{default_tab}");

    const submit = (e) => {{
        e.preventDefault();
        record ? put(`/{url}/${{record.id}}`) : post("/{url}");
    }};

    return (
        <div className="min-h-screen bg-[#f8fafc]">
            {{/* Odoo Top Navigation Bar */}}
            <nav className="bg-[#714B67] text-white px-6 py-2.5 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
                        <span className="text-xl">⠿</span>
                        <span>{app_name}</span>
                    </div>
                    <div className="flex items-center gap-4 text-sm font-medium text-purple-100">
                        <Link href="/{url}" className="hover:text-white transition">{menu_name}</Link>
                    </div>
                </div>
                <div className="flex items-center gap-3 text-xs text-purple-200">
                    <span className="w-7 h-7 rounded-full bg-purple-900/60 border border-purple-400/40 flex items-center justify-center font-bold text-white text-xs">
                        NJ
                    </span>
                </div>
            </nav>

            {{/* Odoo Control Panel */}}
            <div className="bg-white border-b border-gray-200 px-6 py-3 shadow-2xs">
                <div className="max-w-5xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Link href="/{url}" className="text-sm font-medium text-gray-500 hover:text-[#714B67] transition">{model}</Link>
                        <span className="text-gray-300">/</span>
                        <span className="text-sm font-bold text-gray-900">{{record ? (data.{title_name} || record.{title_name} || "Edit") : "New"}}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            type="button"
                            onClick={{submit}}
                            disabled={{processing}}
                            className="rounded bg-[#714B67] hover:bg-[#5a3b52] px-4 py-1.5 text-sm font-semibold text-white shadow-sm transition disabled:opacity-50 flex items-center gap-1.5 cursor-pointer"
                        >
                            {{processing ? "Saving..." : "Save"}}
                        </button>
                        <Link
                            href={{record ? `/{url}/${{record.id}}` : "/{url}"}}
                            className="rounded border border-gray-300 bg-white px-3.5 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-sm transition"
                        >
                            Discard
                        </Link>
                    </div>
                </div>
            </div>

            {{/* Form Sheet Canvas */}}
            <div className="py-6 px-4">
                <div className="max-w-5xl mx-auto bg-white border border-gray-200/90 shadow-2xs rounded-sm p-6 sm:p-10 mb-10">
                    {{/* Smart Buttons Box */}}
                    <div className="flex justify-end mb-6 -mt-2 -mr-2 gap-2">
                        {smart_buttons}
                    </div>

                    {{/* Title Area */}}
                    <div className="mb-6">
                        <label className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-1">{human_label(title_name)}</label>
                        <input
                            type="text"
                            value={{data.{title_name} ?? ""}}
                            onChange={{(e) => setData("{title_name}", e.target.value)}}
                            placeholder="e.g. Internal Website Project"
                            className="text-2xl sm:text-3xl font-bold text-gray-900 border-0 border-b-2 border-gray-200 focus:border-[#714B67] focus:ring-0 px-0 py-1 w-full placeholder:text-gray-300 transition"
                            required
                        />
                        {{errors.{title_name} && <p className="mt-1 text-xs text-red-600">{{errors.{title_name}}}</p>}}
                    </div>

                    {{/* 2-Column Standard Field Grid */}}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-4 mb-8">
                        {scalar_fields}
                    </div>
                    {notebook_jsx}
                </div>
            </div>
        </div>
    );
}}
"""

def generate_show(data):
    model = class_name(data["model"])
    url = data["url"].strip("/")

    menu_parts = (data["menu"] or f"{model}/{model}").split("/")
    app_name = menu_parts[0].strip()
    menu_name = menu_parts[1].strip() if len(menu_parts) > 1 else app_name

    o2m_fields = [f for f in data["fields"] if f["type"].startswith("o2m(")]
    has_description = any(f["name"] == "description" for f in data["fields"])

    default_tab = o2m_fields[0]["name"] if o2m_fields else ("description" if has_description else "")

    title_field = next((f for f in data["fields"] if f["name"] == "name"), None)
    if not title_field:
        title_field = next((f for f in data["fields"] if f["type"] == "char"), None)
    title_name = title_field["name"] if title_field else "name"

    header_buttons = "".join(
        f'\n                    <button type="button" onClick={{() => router.post(`/{url}/${{record.id}}/{action.strip()}`)}} className="rounded bg-[#714B67] px-3.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-[#5a3b52] transition">{action.strip().title()}</button>'
        for action in data["header"]
    )

    smart_buttons = ""
    for o2m in o2m_fields:
        olabel = human_label(o2m["name"])
        smart_buttons += f"""
                    <div className="flex flex-col items-center justify-center border border-gray-200 rounded px-4 py-1.5 bg-gray-50/70 text-right shadow-2xs">
                        <span className="text-xl font-bold text-gray-900 leading-tight">
                            {{record.{o2m['name']}?.length || 0}}
                        </span>
                        <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
                            {olabel}
                        </span>
                    </div>"""

    for smart in data["smart"]:
        slabel = human_label(smart)
        smart_buttons += f"""
                    <div className="flex flex-col items-center justify-center border border-gray-200 rounded px-4 py-1.5 bg-gray-50/70 text-right shadow-2xs">
                        <span className="text-xl font-bold text-gray-900 leading-tight">
                            {{record.{smart.strip()}_count ?? 0}}
                        </span>
                        <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
                            {slabel}
                        </span>
                    </div>"""

    # Scalar detail fields
    detail_items = ""
    for field in data["fields"]:
        fname = field["name"]
        ftype = field["type"]
        if fname in (title_name, "description") or ftype.startswith("o2m(") or field["compute"]:
            continue

        flabel = human_label(fname)

        if ftype == "bool":
            val_expr = f'{{record.{fname} ? <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800">Active</span> : <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">Inactive</span>}}'
        elif ftype.startswith("m2o("):
            val_expr = f'{{record.{fname}?.name ?? record.{fname} ?? "-"}}'
        else:
            val_expr = f'{{record.{fname} ?? "-"}}'

        detail_items += f"""
                <div className="border-b border-gray-100 py-2.5">
                    <dt className="text-xs font-semibold uppercase tracking-wider text-gray-500">{flabel}</dt>
                    <dd className="mt-1 text-sm font-medium text-gray-900">{val_expr}</dd>
                </div>"""

    # Show Notebook tabs
    tab_headers = ""
    tab_contents = ""

    for o2m in o2m_fields:
        olabel = human_label(o2m["name"])
        cols = relation_columns(o2m["type"])

        th_cols = "".join(
            f'\n                                        <th className="px-3 py-2 text-{"center" if col["type"] == "bool" else "left"} text-xs font-semibold text-gray-500 uppercase tracking-wider">{col["label"]}</th>'
            for col in cols
        )

        td_cols = ""
        for col in cols:
            cname = col["name"]
            if col["type"] == "bool":
                td_cols += f'\n                                        <td className="px-3 py-2 text-center">{{line.{cname} ? <span className="text-emerald-700 font-bold">✓ Done</span> : <span className="text-gray-400">Pending</span>}}</td>'
            else:
                td_cols += f'\n                                        <td className="px-3 py-2 text-sm text-gray-700">{{line.{cname} ?? "-"}}</td>'

        col_count = len(cols) + 1

        tab_headers += f"""
                        <button
                            type="button"
                            onClick={{() => setActiveTab("{o2m['name']}")}}
                            className={{`pb-2.5 px-3 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${{
                                activeTab === "{o2m['name']}"
                                    ? "border-[#714B67] text-[#714B67]"
                                    : "border-transparent text-gray-500 hover:text-gray-700"
                            }}`}}
                        >
                            <span>{olabel}</span>
                            <span className="px-1.5 py-0.5 rounded-full text-xs font-bold bg-purple-100 text-[#714B67]">
                                {{record.{o2m['name']}?.length || 0}}
                            </span>
                        </button>"""

        tab_contents += f"""
                    {{activeTab === "{o2m['name']}" && (
                        <div className="border border-gray-200 rounded overflow-hidden shadow-2xs bg-white mt-2">
                            <table className="min-w-full divide-y divide-gray-200 text-sm">
                                <thead className="bg-gray-50/80">
                                    <tr>
                                        <th className="w-12 px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">#</th>{th_cols}
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100 bg-white">
                                    {{(record.{o2m['name']} || []).length > 0 ? (
                                        record.{o2m['name']}.map((line, idx) => (
                                            <tr key={{line.id ?? idx}} className="hover:bg-gray-50/50">
                                                <td className="px-3 py-2 text-xs font-mono text-gray-400">{{idx + 1}}</td>{td_cols}
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan={{{col_count}}} className="px-4 py-8 text-center text-sm text-gray-500">
                                                No {olabel.lower()} recorded for this {model.lower()}.
                                            </td>
                                        </tr>
                                    )}}
                                </tbody>
                            </table>
                        </div>
                    )}}"""

    if has_description:
        tab_headers += f"""
                        <button
                            type="button"
                            onClick={{() => setActiveTab("description")}}
                            className={{`pb-2.5 px-3 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${{
                                activeTab === "description"
                                    ? "border-[#714B67] text-[#714B67]"
                                    : "border-transparent text-gray-500 hover:text-gray-700"
                            }}`}}
                        >
                            Description
                        </button>"""

        tab_contents += f"""
                    {{activeTab === "description" && (
                        <div className="rounded border border-gray-100 bg-gray-50/60 p-4 text-sm text-gray-800 whitespace-pre-wrap mt-2">
                            {{record.description || "No description provided."}}
                        </div>
                    )}}"""

    notebook_jsx = ""
    if o2m_fields or has_description:
        notebook_jsx = f"""
                {{/* Notebook / Tabs */}}
                <div className="mt-8 border-t border-gray-100 pt-6">
                    <div className="flex border-b border-gray-200 space-x-6">
                        {tab_headers}
                    </div>
                    <div className="pt-4">
                        {tab_contents}
                    </div>
                </div>"""

    return f"""import {{ Link, router }} from "@inertiajs/react";
import {{ useState }} from "react";

export default function Show({{ record }}) {{
    const [activeTab, setActiveTab] = useState("{default_tab}");

    return (
        <div className="min-h-screen bg-[#f8fafc]">
            {{/* Odoo Top Navigation Bar */}}
            <nav className="bg-[#714B67] text-white px-6 py-2.5 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
                        <span className="text-xl">⠿</span>
                        <span>{app_name}</span>
                    </div>
                    <div className="flex items-center gap-4 text-sm font-medium text-purple-100">
                        <Link href="/{url}" className="hover:text-white transition">{menu_name}</Link>
                    </div>
                </div>
                <div className="flex items-center gap-3 text-xs text-purple-200">
                    <span className="w-7 h-7 rounded-full bg-purple-900/60 border border-purple-400/40 flex items-center justify-center font-bold text-white text-xs">
                        NJ
                    </span>
                </div>
            </nav>

            {{/* Odoo Control Panel */}}
            <div className="bg-white border-b border-gray-200 px-6 py-3 shadow-2xs">
                <div className="max-w-5xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Link href="/{url}" className="text-sm font-medium text-gray-500 hover:text-[#714B67] transition">{model}</Link>
                        <span className="text-gray-300">/</span>
                        <span className="text-sm font-bold text-gray-900">{{record.{title_name} || "Untitled"}}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Link
                            href={{`/{url}/${{record.id}}/edit`}}
                            className="inline-flex items-center gap-1.5 rounded bg-[#714B67] hover:bg-[#5a3b52] px-4 py-1.5 text-sm font-semibold text-white shadow-sm transition"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                            </svg>
                            Edit
                        </Link>
                        <Link
                            href="/{url}/create"
                            className="rounded border border-gray-300 bg-white px-3.5 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-sm transition"
                        >
                            New
                        </Link>
                        {header_buttons}
                    </div>
                </div>
            </div>

            {{/* Form Sheet Canvas */}}
            <div className="py-6 px-4">
                <div className="max-w-5xl mx-auto bg-white border border-gray-200/90 shadow-2xs rounded-sm p-6 sm:p-10 mb-10">
                    {{/* Smart Buttons Box */}}
                    <div className="flex justify-end mb-6 -mt-2 -mr-2 gap-2">
                        {smart_buttons}
                    </div>

                    {{/* Title Area */}}
                    <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight mb-6">
                        {{record.{title_name} || "Untitled"}}
                    </h1>

                    {{/* 2-Column Fields Grid */}}
                    <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-2 mb-8">
                        {detail_items}
                    </dl>
                    {notebook_jsx}
                </div>
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
            f"resources/js/Components/Generated/One2ManyField.jsx": generate_one2many_component(),
            f"resources/js/Pages/Modules/{self.module}/{model}/Index.jsx": generate_list(self.data),
            f"resources/js/Pages/Modules/{self.module}/{model}/Form.jsx": generate_form(self.data),
            f"resources/js/Pages/Modules/{self.module}/{model}/Show.jsx": generate_show(self.data),
        }

        # Handle child models and migrations for o2m relations
        o2m_fields = [f for f in self.data["fields"] if f["type"].startswith("o2m(")]
        for idx, o2m in enumerate(o2m_fields):
            child_raw = relation_raw_model(o2m["type"])
            child_class = relation_model(o2m["type"])
            child_table = table_name(child_raw)

            child_model_file = f"app/Modules/{self.module}/Model/{child_class}.php"
            files[child_model_file] = generate_child_model(child_raw, self.data, self.module)

            existing_child_migrations = sorted(migration_dir.glob(f"*_create_{child_table}_table.php"))
            if not existing_child_migrations:
                child_timestamp = f"{timestamp}_{idx+1:02d}"
                child_migration_path = migration_dir / f"{child_timestamp}_create_{child_table}_table.php"
                files[str(child_migration_path.relative_to(self.project))] = generate_child_migration(child_raw, self.data)

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
