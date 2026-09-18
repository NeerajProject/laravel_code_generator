from pathlib import Path
from datetime import datetime

# ============================================================
# DSL  (same grammar as the Odoo generator)
# ============================================================

DSL = DSL = """
project:/home/nj/workspace/laravel_code_generator/laravel_code_generator/laraval_caste/my_laravel_app
module:OrderLine

order.line
url:/sales/order-lines

order_id:m2o(sale.order)
product_name:char*
quantity:float
price_unit:float
subtotal:float

list:
    order_id
    product_name
    quantity
    price_unit
    subtotal

filter:
    order_id
    product_name

form:
    order_id
    product_name
    quantity
    price_unit
    subtotal

menu:
    Sales/Order Lines
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
    """sale.order -> App\\Modules\\SaleOrder (or the DSL's module: override)"""
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
# GENERATORS (Model, Migration, Repo, Service, Controller, React views)
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
        return $this->belongsTo(\\App\\Modules\\{relation_class}\\Model\\{relation_class}::class, '{field["name"]}');
    }}
"""
        elif field_type.startswith("o2m("):
            relation_class = relation_model(field_type)
            foreign_key = table.rstrip("s") + "_id"
            relations += f"""
    public function {field["name"]}()
    {{
        return $this->hasMany(\\App\\Modules\\{relation_class}\\Model\\{relation_class}::class, '{foreign_key}');
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
    protected $fillable = [\n        {fillable}\n    ];{casts_block}
    protected $appends = [\n        {appends}\n    ];
{relations}{accessors}
}}
"""

def migration_column(field):
    name = field["name"]
    field_type = field["type"]
    nullable = "" if field["required"] else "->nullable()"

    if field_type.startswith("m2o("):
        return (
            f"            $table->foreignId('{name}')"
            f"{nullable};"
        )
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

    /** Filterable fields for domain-style search: [{domain_hint}] */
    public function all(array $domain = [], array$with = []) {{
        $query = $this->model->newQuery()->with($with);
        foreach ($domain as $field => $value) {{
            if (in_array($field, [{domain_hint}], true) && $value !== null && $value !== '') {{
                $query->where($field, $value);
            }}
        }}
        return $query->latest()->get();
    }}
    public function find($id, array $with = []) {{ return $this->model->with($with)->findOrFail($id); }}
    public function create(array $data) {{ return $this->model->create($data); }}
    public function update($id, array $data) {{$record = $this->find($id);
        $record->update($data);
        return $record;
    }}
    public function delete($id) {{ return $this->find($id)->delete(); }}
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
        return Inertia::render('Modules/{model}/Index', [
            'records' => $this->repository->all($request->get('filters', [])),
        ]);
    }}
    public function create() {{ return Inertia::render('Modules/{model}/Form'); }}
    public function store({model}Request $request) {{
        $this->repository->create($request->validated());
        return redirect()->route('{route_name}.index');
    }}
    public function show($id) {{
        return Inertia::render('Modules/{model}/Show', ['record' => $this->repository->find($id)]);
    }}
    public function edit($id) {{
        return Inertia::render('Modules/{model}/Form', ['record' => $this->repository->find($id)]);
    }}
    public function update({model}Request $request, $id) {{$this->repository->update($id,$request->validated());
        return redirect()->route('{route_name}.index');
    }}
    public function destroy($id) {{
        $this->repository->delete($id);
        return redirect()->route('{route_name}.index');
    }}
{header_actions}
}}
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
    headers = "".join(f"\n                        <th>{f}</th>" for f in data["list"])
    cells = "".join(f"\n                        <td>{{record.{f}}}</td>" for f in data["list"])
    filters = "".join(f'\n            <input placeholder="{f}" onChange={{e => setFilters({{ ...filters, {f}: e.target.value }})}} />' for f in data["filter"])

    return f"""import {{ Link, router }} from "@inertiajs/react";
import {{ useState }} from "react";

export default function Index({{ records }}) {{
    const [filters, setFilters] = useState({{}});
    const applyFilters = () => router.get("/{url}", {{ filters }}, {{ preserveState: true }});

    return (
        <div>
            <h1>{model}</h1>
            <div>{filters}
                <button onClick={{applyFilters}}>Filter</button>
            </div>
            <Link href="/{url}/create">Create</Link>
            <table>
                <thead><tr>{headers}\n                    </tr></thead>
                <tbody>
                    {{records.map(record => (
                        <tr key={{record.id}}>{cells}\n                        </tr>
                    ))}}
                </tbody>
            </table>
        </div>
    );
}}
"""

def generate_form(data):
    model = class_name(data["model"])
    url = data["url"].strip("/")
    inputs = ""
    for field in data["fields"]:
        if field["type"].startswith("o2m(") or field["compute"]: continue
        input_type = "text"
        if field["type"] in ("int", "float"): input_type = "number"
        elif field["type"] == "date": input_type = "date"
        elif field["type"] == "datetime": input_type = "datetime-local"
        elif field["type"] == "bool": input_type = "checkbox"

        inputs += f"""
            <div>
                <label>{field["name"]}</label>
                <input type="{input_type}" value={{data.{field["name"]} ?? ""}} onChange={{e => setData("{field["name"]}", e.target.value)}} />
            </div>"""

    return f"""import {{ useForm }} from "@inertiajs/react";

export default function Form({{ record }}) {{
    const {{ data, setData, post, put, processing }} = useForm(record ?? {{}});
    const submit = (e) => {{
        e.preventDefault();
        record ? put(`/{url}/${{record.id}}`) : post("/{url}");
    }};
    return (
        <form onSubmit={{submit}}>
            <h1>{model}</h1>{inputs}
            <button type="submit" disabled={{processing}}>Save</button>
        </form>
    );
}}
"""

def generate_show(data):
    model = class_name(data["model"])
    url = data["url"].strip("/")
    header_buttons = "".join(f'\n            <button onClick={{() => router.post("/{url}/${{record.id}}/{a.strip()}")}}>{a.strip().title()}</button>' for a in data["header"])
    smart_blocks = "".join(f'\n            <div>{s.strip().title()}: {{record.{s.strip()}_count}}</div>' for s in data["smart"])

    return f"""import {{ router }} from "@inertiajs/react";

export default function Show({{ record }}) {{
    return (
        <div>
            <h1>{model}</h1>{header_buttons}{smart_blocks}
            <pre>{{JSON.stringify(record, null, 2)}}</pre>
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
        self.module_dir = self.project / "app" / "Modules" / self.module

    def register_module_routes(self):
        route_path = self.project / "routes" / "web.php"
        invalid_route_line = (
            f"require __DIR__.'/app/Modules/{self.module}/Routes/web.php';"
        )
        route_line = f"require __DIR__.'/../app/Modules/{self.module}/Routes/web.php';"

        if not route_path.exists():
            route_path.parent.mkdir(parents=True, exist_ok=True)
            route_path.write_text("<?php\n", encoding="utf-8")

        content = route_path.read_text(encoding="utf-8")
        content = content.replace(invalid_route_line, "").replace("\n\n\n", "\n\n")
        if route_line not in content:
            route_path.write_text(content + "\n" + route_line + "\n", encoding="utf-8")
        else:
            route_path.write_text(content, encoding="utf-8")
        print(f"✓ Registered routes: {self.module}")

    def register_repository_binding(self):
        provider_path = self.project / "app" / "Providers" / "AppServiceProvider.php"
        binding = (
            f"        $this->app->bind("
            f"\\App\\Modules\\{self.module}\\Repository\\"
            f"{self.module}RepositoryInterface::class, "
            f"\\App\\Modules\\{self.module}\\Repository\\"
            f"{self.module}Repository::class);"
        )

        content = provider_path.read_text(encoding="utf-8")
        if binding in content:
            return

        register_marker = "    public function register(): void\n    {\n"
        if register_marker not in content:
            raise ValueError(
                f"Cannot register repository binding in {provider_path}: "
                "register method not found."
            )

        content = content.replace(
            register_marker,
            register_marker + binding + "\n",
            1,
        )
        provider_path.write_text(content, encoding="utf-8")
        print(f"✓ Registered repository binding: {self.module}")

    def generate(self):
        if not self.project.exists():
            raise FileNotFoundError(f"Project not found: {self.project}")

        if not (self.project / "artisan").exists():
            raise ValueError("Invalid Laravel project. artisan not found.")

        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        table = table_name(self.data["model"])
        migration_dir = self.project / "database" / "migrations"
        existing_migrations = sorted(
            migration_dir.glob(f"*_create_{table}_table.php")
        )
        migration_path = (
            existing_migrations[-1]
            if existing_migrations
            else migration_dir / f"{timestamp}_create_{table}_table.php"
        )
        migration_relative_path = migration_path.relative_to(self.project)

        # Mapping all files needed for the Laravel project structure.
        files = {
            f"app/Modules/{self.module}/Model/{self.module}.php":
                generate_model(self.data, self.module),
            f"app/Modules/{self.module}/Repository/{self.module}Repository.php":
                generate_repository(self.data, self.module),
            f"app/Modules/{self.module}/Repository/{self.module}RepositoryInterface.php":
                generate_repository_interface(self.data, self.module),
            f"app/Modules/{self.module}/Service/{self.module}Service.php":
                generate_service(self.data, self.module),
            f"app/Modules/{self.module}/Controller/{self.module}Controller.php":
                generate_controller(self.data, self.module),
            f"app/Modules/{self.module}/Request/{self.module}Request.php":
                generate_request(self.data, self.module),
            str(migration_relative_path):
                generate_migration(self.data),
            f"app/Modules/{self.module}/Routes/web.php":
                generate_routes(self.data, self.module),
            f"resources/js/Pages/Modules/{self.module}/Index.jsx":
                generate_list(self.data),
            f"resources/js/Pages/Modules/{self.module}/Form.jsx":
                generate_form(self.data),
            f"resources/js/Pages/Modules/{self.module}/Show.jsx":
                generate_show(self.data),
        }

        for relative_path, content in files.items():
            file_path = self.project / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            print(f"✓ Created: {file_path}")

        self.register_module_routes()
        self.register_repository_binding()
        print(f"\n✓ Module generated: {self.module}\n✓ Location: {self.module_dir}")
        print("\nNext:\ncd", self.project, "\nphp artisan migrate")

if __name__ == "__main__":
    parser = DSLParser(DSL)
    data = parser.parse()
    Generator(data).generate()