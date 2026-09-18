from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

DSL = """
project:/home/nj/workspace/my_laravel_app

sale.order
url:/sales/orders

name:char*
customer_id:m2o(res.partner)
amount_total:float=compute_total
order_line:o2m(order.line)

compute:
    compute_total:
        sum(order_line.subtotal)

header:
    submit

smart:
    invoice
    delivery

list:
    name
    customer_id
    amount_total

filter:
    name
    customer_id

form:
    name
    customer_id
    order_line
    amount_total

menu:
    Sales/Orders
"""


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

            # project
            if stripped.startswith("project:"):
                data["project"] = stripped.split(":", 1)[1]
                continue

            # url
            if stripped.startswith("url:"):
                data["url"] = stripped.split(":", 1)[1]
                continue

            # model
            if not data["model"]:
                data["model"] = stripped
                continue

            # sections
            if stripped in {
                "compute:",
                "header:",
                "smart:",
                "list:",
                "filter:",
                "form:",
                "menu:",
            }:
                section = stripped[:-1]
                compute_name = None
                continue

            # compute method
            if section == "compute":

                if stripped.endswith(":"):
                    compute_name = stripped[:-1]
                    continue

                if compute_name:
                    data["compute"][compute_name] = stripped

                continue

            # field
            if section is None and ":" in stripped:
                self.add_field(data, stripped)
                continue

            # sections
            if section == "header":
                data["header"].append(stripped)

            elif section == "smart":
                data["smart"].append(stripped)

            elif section == "list":
                data["list"].append(stripped)

            elif section == "filter":
                data["filter"].append(stripped)

            elif section == "form":
                data["form"].append(stripped)

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
# HELPERS
# ============================================================

def class_name(model):
    return "".join(
        part.capitalize()
        for part in model.split(".")
    )


def namespace(model):
    return f"App\\Modules\\{class_name(model)}"


def table_name(model):
    return model.replace(".", "_")


# ============================================================
# MODEL
# ============================================================

def generate_model(data):

    model = class_name(data["model"])
    ns = namespace(data["model"])
    table = table_name(data["model"])

    fillable = ",\n        ".join(
        f"'{field['name']}'"
        for field in data["fields"]
    )

    relations = ""

    for field in data["fields"]:

        if field["type"].startswith("m2o("):

            relation = field["type"][4:-1]
            relation_class = class_name(relation)

            relations += f"""
    public function {field["name"]}()
    {{
        return $this->belongsTo(
            \\App\\Models\\{relation_class}::class,
            '{field["name"]}'
        );
    }}
"""

        elif field["type"].startswith("o2m("):

            relation = field["type"][4:-1]
            relation_class = class_name(relation)

            relations += f"""
    public function {field["name"]}()
    {{
        return $this->hasMany(
            \\App\\Models\\{relation_class}::class
        );
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
    ];

{relations}
}}
"""


# ============================================================
# REPOSITORY
# ============================================================

def generate_repository(data):

    model = class_name(data["model"])
    ns = namespace(data["model"])

    return f"""<?php

namespace {ns}\\Repository;

use {ns}\\Model\\{model};

class {model}Repository
{{
    public function __construct(
        protected {model} $model
    ) {{}}

    public function all()
    {{
        return $this->model->latest()->get();
    }}

    public function find($id)
    {{
        return $this->model->findOrFail($id);
    }}

    public function create(array $data)
    {{
        return $this->model->create($data);
    }}

    public function update($id, array $data)
    {{
        $record = $this->find($id);

        $record->update($data);

        return $record;
    }}

    public function delete($id)
    {{
        return $this->find($id)->delete();
    }}
}}
"""


def generate_repository_interface(data):

    model = class_name(data["model"])
    ns = namespace(data["model"])

    return f"""<?php

namespace {ns}\\Repository;

interface {model}RepositoryInterface
{{
    public function all();

    public function find($id);

    public function create(array $data);

    public function update($id, array $data);

    public function delete($id);
}}
"""


# ============================================================
# SERVICE
# ============================================================

def generate_service(data):

    model = class_name(data["model"])
    ns = namespace(data["model"])

    methods = ""

    actions = set(
        data["header"] +
        data["smart"]
    )

    for action in actions:

        method = action.replace("-", "_")

        methods += f"""
    public function {method}($id)
    {{
        return $this->repository->find($id);
    }}

"""

    return f"""<?php

namespace {ns}\\Service;

use {ns}\\Repository\\{model}Repository;

class {model}Service
{{
    public function __construct(
        protected {model}Repository $repository
    ) {{}}

{methods}
}}
"""


# ============================================================
# CONTROLLER
# ============================================================

def generate_controller(data):

    model = class_name(data["model"])
    ns = namespace(data["model"])

    return f"""<?php

namespace {ns}\\Controller;

use App\\Http\\Controllers\\Controller;
use Illuminate\\Http\\Request;
use Inertia\\Inertia;
use {ns}\\Repository\\{model}Repository;
use {ns}\\Service\\{model}Service;

class {model}Controller extends Controller
{{
    public function __construct(
        protected {model}Repository $repository,
        protected {model}Service $service
    ) {{}}

    public function index()
    {{
        return Inertia::render(
            'Modules/{model}/Index',
            [
                'records' => $this->repository->all(),
            ]
        );
    }}

    public function create()
    {{
        return Inertia::render(
            'Modules/{model}/Form'
        );
    }}

    public function store(Request $request)
    {{
        $this->repository->create(
            $request->all()
        );

        return redirect()->route(
            '{data["model"]}.index'
        );
    }}

    public function show($id)
    {{
        return Inertia::render(
            'Modules/{model}/Show',
            [
                'record' =>
                    $this->repository->find($id),
            ]
        );
    }}

    public function edit($id)
    {{
        return Inertia::render(
            'Modules/{model}/Form',
            [
                'record' =>
                    $this->repository->find($id),
            ]
        );
    }}

    public function update(
        Request $request,
        $id
    )
    {{
        $this->repository->update(
            $id,
            $request->all()
        );

        return redirect()->route(
            '{data["model"]}.index'
        );
    }}

    public function destroy($id)
    {{
        $this->repository->delete($id);

        return redirect()->route(
            '{data["model"]}.index'
        );
    }}
}}
"""


# ============================================================
# REQUEST
# ============================================================

def generate_request(data):

    model = class_name(data["model"])
    ns = namespace(data["model"])

    rules = []

    for field in data["fields"]:

        required = "required" \
            if field["required"] \
            else "nullable"

        rules.append(
            f"            '{field['name']}' => '{required}',"
        )

    return f"""<?php

namespace {ns}\\Request;

use Illuminate\\Foundation\\Http\\FormRequest;

class {model}Request extends FormRequest
{{
    public function authorize(): bool
    {{
        return true;
    }}

    public function rules(): array
    {{
        return [
{chr(10).join(rules)}
        ];
    }}
}}
"""


# ============================================================
# ROUTES
# ============================================================

def generate_routes(data):

    model = class_name(data["model"])
    ns = namespace(data["model"])

    url = data["url"].lstrip("/")

    return f"""<?php

use Illuminate\\Support\\Facades\\Route;
use {ns}\\Controller\\{model}Controller;

Route::resource(
    '{url}',
    {model}Controller::class
)->names('{data["model"]}');
"""


# ============================================================
# INERTIA LIST
# ============================================================

def generate_list(data):

    model = class_name(data["model"])

    columns = ""

    for field in data["list"]:
        columns += f"""
                    <th>{field}</th>"""

    rows = ""

    for field in data["list"]:
        rows += f"""
                        <td>{{record.{field}}}</td>"""

    return f"""import {{ Link }} from "@inertiajs/react";

export default function Index({{ records }}) {{

    return (
        <div>

            <h1>{model}</h1>

            <Link
                href="/{data["url"].strip("/")}/create"
            >
                Create
            </Link>

            <table>

                <thead>
                    <tr>
{columns}
                    </tr>
                </thead>

                <tbody>

                    {{records.map(record => (

                        <tr key={{record.id}}>
{rows}
                        </tr>

                    ))}}

                </tbody>

            </table>

        </div>
    );
}}
"""


# ============================================================
# INERTIA FORM
# ============================================================

def generate_form(data):

    model = class_name(data["model"])

    inputs = ""

    for field in data["fields"]:

        inputs += f"""
            <div>
                <label>{field["name"]}</label>

                <input
                    name="{field["name"]}"
                    defaultValue={{record?.{field["name"]} ?? ""}}
                />
            </div>
"""

    return f"""export default function Form({{ record }}) {{

    return (

        <form>

            <h1>{model}</h1>

{inputs}

            <button type="submit">
                Save
            </button>

        </form>

    );
}}
"""


# ============================================================
# INERTIA SHOW
# ============================================================

def generate_show(data):

    model = class_name(data["model"])

    return f"""export default function Show({{ record }}) {{

    return (

        <div>

            <h1>{model}</h1>

            <pre>
                {{JSON.stringify(
                    record,
                    null,
                    2
                )}}
            </pre>

        </div>

    );
}}
"""


# ============================================================
# MAIN GENERATOR
# ============================================================

class Generator:

    def __init__(self, data):

        self.data = data

        self.project = (
            Path(data["project"])
            .expanduser()
            .resolve()
        )

        self.module = class_name(
            data["model"]
        )

        self.module_dir = (
            self.project
            / "app"
            / "Modules"
            / self.module
        )

    def generate(self):

        if not self.project.exists():
            raise FileNotFoundError(
                f"Project not found: {self.project}"
            )

        if not (self.project / "artisan").exists():
            raise ValueError(
                "Invalid Laravel project: artisan not found"
            )

        files = {

            f"Model/{self.module}.php":
                generate_model(self.data),

            f"Repository/{self.module}Repository.php":
                generate_repository(self.data),

            f"Repository/{self.module}RepositoryInterface.php":
                generate_repository_interface(self.data),

            f"Service/{self.module}Service.php":
                generate_service(self.data),

            f"Controller/{self.module}Controller.php":
                generate_controller(self.data),

            f"Request/{self.module}Request.php":
                generate_request(self.data),

            "Routes/web.php":
                generate_routes(self.data),

            "Resources/js/Index.jsx":
                generate_list(self.data),

            "Resources/js/Form.jsx":
                generate_form(self.data),

            "Resources/js/Show.jsx":
                generate_show(self.data),
        }

        for relative_path, content in files.items():

            file_path = (
                self.module_dir
                / relative_path
            )

            file_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            file_path.write_text(
                content,
                encoding="utf-8"
            )

            print(
                f"Created: {file_path}"
            )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    parser = DSLParser(DSL)

    data = parser.parse()

    Generator(data).generate()