import os
import re
from datetime import datetime, timedelta


# ============================================================
# DSL
# ============================================================

DSL = r'''
project = "/home/nj/workspace/laravel_code_generator/laravel_code_generator/laraval_caste/my_laravel_app"
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
'''


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def pascal_case(value):
    parts = re.split(r'[._\-\s]+', value)
    return ''.join(part[:1].upper() + part[1:] for part in parts if part)


def snake_case(value):
    value = value.replace('.', '_').replace('-', '_')
    value = re.sub(r'(?<!^)(?=[A-Z])', '_', value)
    value = re.sub(r'[^a-zA-Z0-9_]', '_', value)
    return value.lower().strip('_')


def table_name(model_name):
    name = snake_case(model_name)
    return name if name.endswith('s') else name + 's'


def label(value):
    return value.replace('_', ' ').replace('.', ' ').title()


def field_type(field):
    return field['type']


def is_m2o(field):
    return field_type(field).startswith('m2o(')


def is_o2m(field):
    return field_type(field).startswith('o2m(')


def is_selection(field):
    return field_type(field).startswith('selection(')


def relation_model(field):
    match = re.match(r'(?:m2o|o2m)\(([^)]+)\)', field_type(field))
    return match.group(1).strip() if match else None


def relation_method_name(field_name):
    """Strips trailing _id for Eloquent belongsTo relation methods to avoid attribute collisions."""
    if field_name.endswith('_id'):
        return field_name[:-3]
    return field_name


def foreign_key_col(field_name):
    if field_name.endswith('_id'):
        return field_name
    return f"{field_name}_id"


def selection_values(field):
    match = re.match(r'selection\(([^)]*)\)', field_type(field))
    if not match:
        return []
    return [v.strip() for v in match.group(1).split(',') if v.strip()]


def is_computed(field):
    return bool(field.get('compute'))


def laravel_cast(field):
    value = field_type(field)
    casts = {
        'bool': 'boolean',
        'float': 'float',
        'integer': 'integer',
        'date': 'date',
        'datetime': 'datetime',
    }
    return casts.get(value)


# ============================================================
# DSL PARSER
# ============================================================

def parse_dsl(dsl):
    project = None
    module = None
    models = []

    current_model = None
    current_section = None
    current_compute = None

    for raw_line in dsl.splitlines():
        if not raw_line.strip():
            continue

        stripped = raw_line.strip()
        indent = len(raw_line) - len(raw_line.lstrip())

        project_match = re.match(r'^project\s*(?::|=)\s*(.+)$', stripped)
        if project_match:
            project = project_match.group(1).strip().strip('"\'')
            continue

        if stripped.startswith('module:'):
            module = stripped.split(':', 1)[1].strip()
            continue

        # MODEL HEADER
        if indent == 0 and ':' not in stripped and not stripped.endswith(':'):
            current_model = {
                'name': stripped,
                'url': None,
                'fields': {},
                'list': [],
                'filter': [],
                'form': [],
                'compute': {},
                'menu': None,
                'master': False,
            }
            models.append(current_model)
            current_section = None
            current_compute = None
            continue

        if current_model is None:
            continue

        if stripped.startswith('url:'):
            current_model['url'] = stripped.split(':', 1)[1].strip()
            current_section = None
            current_compute = None
            continue

        if stripped in ('list:', 'filter:', 'form:', 'compute:', 'menu:'):
            current_section = stripped[:-1]
            current_compute = None
            continue

        if current_section == 'menu':
            current_model['menu'] = stripped
            continue

        if current_section == 'compute':
            if ':' in stripped and not stripped.endswith(':'):
                c_name, c_expr = stripped.split(':', 1)
                current_model['compute'][c_name.strip()] = c_expr.strip()
            elif stripped.endswith(':'):
                current_compute = stripped[:-1].strip()
                current_model['compute'][current_compute] = ''
            elif current_compute:
                current_model['compute'][current_compute] = stripped
            continue

        if current_section in ('list', 'filter', 'form'):
            current_model[current_section].append(stripped)
            continue

        # FIELD DEFINITION
        if current_section is None and ':' in stripped:
            name, definition = stripped.split(':', 1)
            required = definition.endswith('*')
            definition = definition.rstrip('*')
            compute = None

            if '=' in definition:
                definition, compute = definition.split('=', 1)
                compute = compute.strip()

            current_model['fields'][name.strip()] = {
                'name': name.strip(),
                'type': definition.strip(),
                'required': required,
                'compute': compute,
            }

    return {
        'project': project,
        'module': module,
        'models': models,
    }


# ============================================================
# GENERATOR
# ============================================================

class Generator:

    def __init__(self, data):
        self.project = data['project']
        self.module = data['module']
        self.models = data['models']
        self.model_map = {model['name']: model for model in self.models}
        self.migration_index = 0
        self.add_missing_relation_models()

    def mkdir(self, path):
        os.makedirs(path, exist_ok=True)

    def write(self, path, content):
        directory = os.path.dirname(path)
        if directory:
            self.mkdir(directory)
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
        print('CREATED:', path)

    def add_missing_relation_models(self):
        needed = []
        for model in self.models:
            for field in model['fields'].values():
                if is_m2o(field) or is_o2m(field):
                    target = relation_model(field)
                    if target and target not in self.model_map:
                        needed.append(target)

        for target in needed:
            if target in self.model_map:
                continue
            model = {
                'name': target,
                'url': '/' + table_name(target).replace('_', '-'),
                'fields': {
                    'name': {
                        'name': 'name',
                        'type': 'char',
                        'required': False,
                        'compute': None,
                    }
                },
                'list': ['name'],
                'filter': ['name'],
                'form': ['name'],
                'compute': {},
                'menu': None,
                'master': True,
            }
            self.models.append(model)
            self.model_map[target] = model
            print('AUTO MASTER MODEL:', target)

    def model_path(self, model):
        return os.path.join(self.project, 'app', 'Models', pascal_case(model['name']) + '.php')

    def controller_path(self, model):
        return os.path.join(self.project, 'app', 'Http', 'Controllers', pascal_case(model['name']) + 'Controller.php')

    def page_dir(self, model):
        return os.path.join(self.project, 'resources', 'js', 'Pages', self.module, pascal_case(model['name']))

    def migration_path(self, model):
        self.migration_index += 1
        timestamp = datetime.now() + timedelta(seconds=self.migration_index)
        prefix = timestamp.strftime('%Y_%m_%d_%H%M%S')
        return os.path.join(
            self.project,
            'database',
            'migrations',
            f"{prefix}_create_{table_name(model['name'])}_table.php"
        )

    def inverse_fk(self, parent_name, child_model):
        for field in child_model['fields'].values():
            if is_m2o(field) and relation_model(field) == parent_name:
                return foreign_key_col(field['name'])
        return snake_case(parent_name) + '_id'

    def dependency_order(self):
        result = []
        visiting = set()
        visited = set()

        def visit(name):
            if name in visited or name in visiting:
                return
            visiting.add(name)
            model = self.model_map[name]
            for field in model['fields'].values():
                if not is_m2o(field):
                    continue
                target = relation_model(field)
                if target in self.model_map and target != name:
                    visit(target)
            visiting.remove(name)
            visited.add(name)
            result.append(name)

        for model in self.models:
            visit(model['name'])

        return [self.model_map[name] for name in result]

    def relation_names(self, model):
        relations = []
        for field in model['fields'].values():
            if is_m2o(field):
                relations.append(relation_method_name(field['name']))
            elif is_o2m(field):
                relations.append(field['name'])
        return relations

    def relation_data_fields(self, model):
        fields = []
        for field in model['fields'].values():
            if is_m2o(field):
                fields.append(field)
            elif is_o2m(field):
                child = self.model_map[relation_model(field)]
                for child_field in child['fields'].values():
                    if is_m2o(child_field):
                        fields.append(child_field)

        result = []
        seen = set()
        for field in fields:
            if field['name'] not in seen:
                seen.add(field['name'])
                result.append(field)
        return result

    # ========================================================
    # MODEL GENERATION
    # ========================================================

    def generate_model(self, model):
        class_name = pascal_case(model['name'])
        lines = [
            '<?php',
            '',
            'namespace App\\Models;',
            '',
            'use Illuminate\\Database\\Eloquent\\Model;',
            'use Illuminate\\Database\\Eloquent\\Relations\\BelongsTo;',
            'use Illuminate\\Database\\Eloquent\\Relations\\HasMany;',
            '',
            f'class {class_name} extends Model',
            '{',
            f"    protected $table = '{table_name(model['name'])}';",
            '',
            '    protected $fillable = [',
        ]

        for field in model['fields'].values():
            if not is_o2m(field):
                col_name = foreign_key_col(field['name']) if is_m2o(field) else field['name']
                lines.append(f"        '{col_name}',")

        lines.append('    ];')

        casts = []
        for field in model['fields'].values():
            cast = laravel_cast(field)
            if cast:
                lines.append(f"        '{field['name']}' => '{cast}',")

        if casts:
            lines += ['', '    protected $casts = [', *casts, '    ];']

        for field in model['fields'].values():
            if is_m2o(field):
                target = pascal_case(relation_model(field))
                field_name = field['name']
                method = relation_method_name(field_name)
                fk = foreign_key_col(field_name)
                lines += [
                    '',
                    f'    public function {method}(): BelongsTo',
                    '    {',
                    f"        return $this->belongsTo({target}::class, '{fk}');",
                    '    }',
                ]
            elif is_o2m(field):
                target_name = relation_model(field)
                child = self.model_map[target_name]
                target = pascal_case(target_name)
                foreign_key = self.inverse_fk(model['name'], child)
                name = field['name']
                lines += [
                    '',
                    f'    public function {name}(): HasMany',
                    '    {',
                    f"        return $this->hasMany({target}::class, '{foreign_key}');",
                    '    }',
                ]

        lines += ['}', '']
        self.write(self.model_path(model), '\n'.join(lines))

    # ========================================================
    # MIGRATION GENERATION
    # ========================================================

    def generate_migration(self, model):
        table = table_name(model['name'])
        lines = [
            '<?php',
            '',
            'use Illuminate\\Database\\Migrations\\Migration;',
            'use Illuminate\\Database\\Schema\\Blueprint;',
            'use Illuminate\\Support\\Facades\\Schema;',
            '',
            'return new class extends Migration',
            '{',
            '    public function up(): void',
            '    {',
            f"        Schema::create('{table}', function (Blueprint $table) {{",
            '            $table->id();',
        ]

        for field in model['fields'].values():
            name = field['name']
            value_type = field_type(field)

            if name == 'id' or is_o2m(field):
                continue

            if is_m2o(field):
                target = relation_model(field)
                fk = foreign_key_col(name)
                lines.append(
                    f"            $table->foreignId('{fk}')"
                    f"->nullable()->constrained('{table_name(target)}')"
                    f"->nullOnDelete();"
                )
            elif is_selection(field):
                values = selection_values(field)
                max_length = max([len(v) for v in values] + [50])
                lines.append(f"            $table->string('{name}', {max_length})->nullable();")
            elif value_type == 'char':
                nullable = '' if field['required'] else '->nullable()'
                lines.append(f"            $table->string('{name}'){nullable};")
            elif value_type == 'text':
                lines.append(f"            $table->text('{name}')->nullable();")
            elif value_type == 'float':
                lines.append(f"            $table->decimal('{name}', 16, 4)->default(0);")
            elif value_type == 'integer':
                lines.append(f"            $table->integer('{name}')->default(0);")
            elif value_type == 'bool':
                lines.append(f"            $table->boolean('{name}')->default(false);")
            elif value_type == 'date':
                lines.append(f"            $table->date('{name}')->nullable();")
            elif value_type == 'datetime':
                lines.append(f"            $table->dateTime('{name}')->nullable();")
            else:
                lines.append(f"            $table->string('{name}')->nullable();")

        lines += [
            '            $table->timestamps();',
            '        });',
            '    }',
            '',
            '    public function down(): void',
            '    {',
            f"        Schema::dropIfExists('{table}');",
            '    }',
            '};',
            '',
        ]
        self.write(self.migration_path(model), '\n'.join(lines))

    # ========================================================
    # CONTROLLER COMPUTATIONS & O2M LOGIC
    # ========================================================

    def compute_child_expression(self, model):
        for field in model['fields'].values():
            if not is_computed(field):
                continue

            expression = model['compute'].get(field['compute'], '')
            match = re.fullmatch(r'(\w+)\s*([\+\-\*\/])\s*(\w+)', expression)
            if match:
                first, op, second = match.groups()
                return (
                    field['name'],
                    f"($lineData['{first}'] ?? 0) {op} ($lineData['{second}'] ?? 0)"
                )
        return None, None

    def o2m_save_lines(self, model, parent_variable, indent):
        lines = []
        for field in model['fields'].values():
            if not is_o2m(field):
                continue

            relation = field['name']
            child_name = relation_model(field)
            child = self.model_map[child_name]
            child_class = pascal_case(child_name)
            foreign_key = self.inverse_fk(model['name'], child)

            lines += [
                '',
                f"{indent}foreach ($request->input('{relation}', []) as $lineData) {{",
                f"{indent}    $lineData['{foreign_key}'] = {parent_variable}->id;",
            ]

            computed_name, expression = self.compute_child_expression(child)
            if computed_name:
                lines.append(f"{indent}    $lineData['{computed_name}'] = {expression};")

            lines += [
                f"{indent}    {child_class}::create($lineData);",
                f"{indent}}}",
            ]
        return lines

    def parent_compute_lines(self, model, parent_variable, indent):
        lines = []
        for field in model['fields'].values():
            if not is_computed(field):
                continue

            expression = model['compute'].get(field['compute'], '')
            match = re.fullmatch(r'sum\((\w+)\.(\w+)\)', expression)
            if match:
                relation, child_field = match.groups()
                lines += [
                    '',
                    f"{indent}{parent_variable}->update([",
                    f"{indent}    '{field['name']}' => {parent_variable}->{relation}()->sum('{child_field}'),",
                    f"{indent}]);",
                ]
        return lines

    # ========================================================
    # CONTROLLER GENERATION
    # ========================================================

    def generate_controller(self, model):
        class_name = pascal_case(model['name'])
        imports = [
            'use Illuminate\\Http\\Request;',
            'use Illuminate\\Support\\Facades\\DB;',
            'use Inertia\\Inertia;',
            f"use App\\Models\\{class_name};",
        ]

        imported = {class_name}
        for field in self.relation_data_fields(model):
            target = pascal_case(relation_model(field))
            if target not in imported:
                imports.append(f"use App\\Models\\{target};")
                imported.add(target)

        lines = [
            '<?php',
            '',
            'namespace App\\Http\\Controllers;',
            '',
            *imports,
            '',
            f"class {class_name}Controller extends Controller",
            '{',
            '    public function index(Request $request)',
            '    {',
            f"        $query = {class_name}::query();",
        ]

        relations = self.relation_names(model)
        if relations:
            rel_str = ", ".join(f"'{name}'" for name in relations)
            lines.append(f"        $query->with([{rel_str}]);")

        lines += [
            '',
            "        if ($request->filled('search')) {",
            "            $search = $request->search;",
            "            $query->where(function ($q) use ($search) {",
        ]

        searchable = [
            field['name'] for field in model['fields'].values()
            if field_type(field) in ('char', 'text')
        ]

        for index, name in enumerate(searchable):
            method = 'where' if index == 0 else 'orWhere'
            lines.append(f"                $q->{method}('{name}', 'like', '%' . $search . '%');")

        if not searchable:
            lines.append("                $q->whereKey(0);")

        lines += [
            '            });',
            '        }',
            '',
            "        $records = $query->latest()->paginate(20)->withQueryString();",
            '',
            f"        return Inertia::render('{self.module}/{class_name}/Index', ['records' => $records]);",
            '    }',
            '',
            '    public function create()',
            '    {',
            '        return Inertia::render(',
            f"            '{self.module}/{class_name}/Form',",
            '            [',
            "                'record' => null,",
            "                'relations' => $this->relationData(),",
            '            ]',
            '        );',
            '    }',
            '',
            '    public function store(Request $request)',
            '    {',
            "        return DB::transaction(function () use ($request) {",
            "            $data = $request->except(['_token']);",
        ]

        for field in model['fields'].values():
            if is_o2m(field) or is_computed(field):
                lines.append(f"            unset($data['{field['name']}']);")

        lines.append(f"            $record = {class_name}::create($data);")
        lines += self.o2m_save_lines(model, '$record', '            ')
        lines += self.parent_compute_lines(model, '$record', '            ')

        route_name = snake_case(model['name'])
        lines += [
            '',
            f"            return redirect()->route('{route_name}.index')->with('success', 'Created successfully.');",
            '        });',
            '    }',
            '',
            f"    public function show({class_name} $record)",
            '    {',
            "        $record->load($this->relations());",
            f"        return Inertia::render('{self.module}/{class_name}/Form', [",
            "            'record' => $record,",
            "            'relations' => $this->relationData(),",
            "            'readonly' => true,",
            '        ]);',
            '    }',
            '',
            f"    public function edit({class_name} $record)",
            '    {',
            "        $record->load($this->relations());",
            f"        return Inertia::render('{self.module}/{class_name}/Form', [",
            "            'record' => $record,",
            "            'relations' => $this->relationData(),",
            '        ]);',
            '    }',
            '',
            f"    public function update(Request $request, {class_name} $record)",
            '    {',
            "        return DB::transaction(function () use ($request, $record) {",
            "            $data = $request->except(['_token', '_method']);",
        ]

        for field in model['fields'].values():
            if is_o2m(field) or is_computed(field):
                lines.append(f"            unset($data['{field['name']}']);")

        lines.append("            $record->update($data);")

        for field in model['fields'].values():
            if is_o2m(field):
                lines.append(f"            $record->{field['name']}()->delete();")

        lines += self.o2m_save_lines(model, '$record', '            ')
        lines += self.parent_compute_lines(model, '$record', '            ')

        relation_names = ", ".join(f'"{name}"' for name in relations)
        lines += [
            '',
            f"            return redirect()->route('{route_name}.index')->with('success', 'Updated successfully.');",
            '        });',
            '    }',
            '',
            f"    public function destroy({class_name} $record)",
            '    {',
            '        $record->delete();',
            "        return redirect()->back()->with('success', 'Deleted successfully.');",
            '    }',
            '',
            '    private function relations(): array',
            '    {',
            f"        return [{relation_names}];",
            '    }',
            '',
            '    private function relationData(): array',
            '    {',
            '        $relations = [];',
        ]

        for field in self.relation_data_fields(model):
            target = pascal_case(relation_model(field))
            fname = field['name']
            lines.append(f"        $relations['{fname}'] = {target}::orderBy('name')->get(['id', 'name']);")

        lines += [
            '        return $relations;',
            '    }',
            '}',
            '',
        ]
        self.write(self.controller_path(model), '\n'.join(lines))

    # ========================================================
    # INERTIA INDEX REACT COMPONENT
    # ========================================================

    def generate_index(self, model):
        path = os.path.join(self.page_dir(model), 'Index.jsx')
        url = model['url']

        lines = [
            "import React, { useState } from 'react';",
            "import { Head, Link, router } from '@inertiajs/react';",
            '',
            "export default function Index({ records }) {",
            "    const [search, setSearch] = useState('');",
            '',
            "    const submitSearch = (e) => {",
            "        e.preventDefault();",
            f"        router.get('{url}', {{ search }}, {{ preserveState: true, replace: true }});",
            "    };",
            '',
            "    const remove = (id) => {",
            "        if (!confirm('Delete this record?')) return;",
            f"        router.delete(`${url}/${{id}}`);",
            "    };",
            '',
            '    return (',
            '        <div className="p-6">',
            f'            <Head title="{label(model["name"])}" />',
            '            <div className="flex justify-between mb-6">',
            f'                <h1 className="text-2xl font-bold">{label(model["name"])}</h1>',
            f'                <Link href="{url}/create" className="px-4 py-2 bg-blue-600 text-white rounded">Create</Link>',
            '            </div>',
            '            <form onSubmit={submitSearch} className="mb-4 flex gap-2">',
            '                <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search..." className="border rounded px-3 py-2" />',
            '                <button className="border px-4 py-2 rounded">Search</button>',
            '            </form>',
            '            <div className="overflow-x-auto">',
            '                <table className="w-full border">',
            '                    <thead>',
            '                        <tr>',
        ]

        for field_name in model['list']:
            lines.append(f'                            <th className="border p-2 text-left">{label(field_name)}</th>')

        lines += [
            '                            <th className="border p-2">Actions</th>',
            '                        </tr>',
            '                    </thead>',
            '                    <tbody>',
            '                        {records.data.map((row) => (',
            '                            <tr key={row.id}>',
        ]

        for field_name in model['list']:
            field = model['fields'].get(field_name)
            if field and is_m2o(field):
                rel = relation_method_name(field_name)
                value = f"row.{rel}?.name || row.{field_name} || '-'"
            else:
                value = f"row.{field_name} ?? '-'"

            lines.append(f'                                <td className="border p-2">{{{value}}}</td>')

        lines += [
            '                                <td className="border p-2">',
            f'                                    <Link href={{`{url}/${{row.id}}/edit`}} className="mr-3 text-blue-600">Edit</Link>',
            '                                    <button onClick={() => remove(row.id)} className="text-red-600">Delete</button>',
            '                                </td>',
            '                            </tr>',
            '                        ))}',
            '                    </tbody>',
            '                </table>',
            '            </div>',
            '        </div>',
            '    );',
            '}',
            '',
        ]
        self.write(path, '\n'.join(lines))

    # ========================================================
    # INERTIA FORM REACT COMPONENT
    # ========================================================

    def generate_form(self, model):
        path = os.path.join(self.page_dir(model), 'Form.jsx')
        url = model['url']

        lines = [
            "import React from 'react';",
            "import { Head, Link, useForm } from '@inertiajs/react';",
            '',
            "export default function Form({ record, relations = {}, readonly = false }) {",
            "    const isEdit = !!record?.id;",
            '',
            "    const { data, setData, post, put, processing } = useForm({",
        ]

        for field_name in model['form']:
            field = model['fields'].get(field_name)
            if not field:
                continue

            if is_o2m(field):
                lines.append(f"        {field_name}: record?.{field_name} || [],")
            elif is_m2o(field):
                rel = relation_method_name(field_name)
                lines.append(f"        {field_name}: record?.{field_name} ?? record?.{rel}?.id ?? '',")
            elif field_type(field) == 'bool':
                lines.append(f"        {field_name}: record?.{field_name} ?? false,")
            else:
                lines.append(f"        {field_name}: record?.{field_name} ?? '',")

        lines += [
            '    });',
            '',
            '    const submit = (e) => {',
            '        e.preventDefault();',
            '        if (isEdit) {',
            f"            put(`${url}/${{record.id}}`);",
            '        } else {',
            f"            post('{url}');",
            '        }',
            '    };',
        ]

        for field in model['fields'].values():
            if not is_o2m(field):
                continue

            relation = field['name']
            child = self.model_map[relation_model(field)]
            func_name = 'add' + pascal_case(relation)

            lines += [
                '',
                f"    const {func_name} = () => {{",
                f"        setData('{relation}', [...(data.{relation} || []), {{",
            ]

            for child_name in child['form']:
                child_field = child['fields'].get(child_name)
                if child_field and not is_computed(child_field):
                    lines.append(f"            {child_name}: '',")

            lines += ['        }]);', '    };']

        lines += [
            '',
            '    return (',
            '        <div className="p-6 max-w-6xl mx-auto">',
            f'            <Head title="{label(model["name"])}" />',
            '            <div className="flex justify-between mb-6">',
            f'                <h1 className="text-2xl font-bold">{{isEdit ? \'Edit\' : \'Create\'}} {label(model["name"])}</h1>',
            f'                <Link href="{url}" className="border px-4 py-2 rounded">Back</Link>',
            '            </div>',
            '            <form onSubmit={submit} className="space-y-5">',
        ]

        for field_name in model['form']:
            field = model['fields'].get(field_name)
            if not field:
                continue

            if is_o2m(field):
                child = self.model_map[relation_model(field)]
                func_name = 'add' + pascal_case(field_name)

                lines += [
                    '',
                    '                <div className="border rounded p-4">',
                    '                    <div className="flex justify-between mb-3">',
                    f'                        <h2 className="font-semibold">{label(field_name)}</h2>',
                    f'                        {{!readonly && <button type="button" onClick={{{func_name}}} className="border px-3 py-1 rounded">Add Line</button>}}',
                    '                    </div>',
                    f'                    {{(data.{field_name} || []).map((line, index) => (',
                    '                        <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">',
                ]

                for child_name in child['form']:
                    child_field = child['fields'].get(child_name)
                    if not child_field:
                        continue

                    if is_m2o(child_field):
                        lines += [
                            f'                            <select value={{line.{child_name} ?? \'\'}} disabled={{readonly}} onChange={{(e) => {{ const copy = [...data.{field_name}]; copy[index] = {{ ...copy[index], {child_name}: e.target.value }}; setData(\'{field_name}\', copy); }}}} className="border rounded px-2 py-1">',
                            f'                                <option value="">{label(child_name)}</option>',
                            f'                                {{(relations[\'{child_name}\'] || []).map((item) => (',
                            '                                    <option key={item.id} value={item.id}>{item.name}</option>',
                            '                                ))}',
                            '                            </select>',
                        ]
                    elif is_computed(child_field):
                        lines.append(f'                            <input value={{line.{child_name} ?? \'\'}} readOnly className="border rounded px-2 py-1 bg-gray-100" placeholder="{label(child_name)}" />')
                    else:
                        child_type = field_type(child_field)
                        input_type = 'number' if child_type in ('float', 'integer') else ('date' if child_type == 'date' else 'text')
                        lines.append(f'                            <input type="{input_type}" value={{line.{child_name} ?? \'\'}} disabled={{readonly}} onChange={{(e) => {{ const copy = [...data.{field_name}]; copy[index] = {{ ...copy[index], {child_name}: e.target.value }}; setData(\'{field_name}\', copy); }}}} className="border rounded px-2 py-1" placeholder="{label(child_name)}" />')

                lines += [
                    '                        </div>',
                    '                    ))}',
                    '                </div>',
                ]
                continue

            lines += [
                '',
                '                <div>',
                f'                    <label className="block mb-1 font-medium">{label(field_name)}</label>',
            ]

            if is_m2o(field):
                lines += [
                    f'                    <select value={{data.{field_name}}} disabled={{readonly}} onChange={{(e) => setData(\'{field_name}\', e.target.value)}} className="border rounded px-3 py-2 w-full">',
                    '                        <option value="">Select...</option>',
                    f'                        {{(relations[\'{field_name}\'] || []).map((item) => (',
                    '                            <option key={item.id} value={item.id}>{item.name}</option>',
                    '                        ))}',
                    '                    </select>',
                ]
            elif is_selection(field):
                lines.append(f'                    <select value={{data.{field_name}}} disabled={{readonly}} onChange={{(e) => setData(\'{field_name}\', e.target.value)}} className="border rounded px-3 py-2 w-full">')
                lines.append('                        <option value="">Select...</option>')
                for val in selection_values(field):
                    lines.append(f'                        <option value="{val}">{label(val)}</option>')
                lines.append('                    </select>')
            elif field_type(field) == 'bool':
                lines.append(f'                    <input type="checkbox" checked={{!!data.{field_name}}} disabled={{readonly}} onChange={{(e) => setData(\'{field_name}\', e.target.checked)}} />')
            elif field_type(field) == 'text':
                lines.append(f'                    <textarea value={{data.{field_name}}} readOnly={{readonly}} onChange={{(e) => setData(\'{field_name}\', e.target.value)}} className="border rounded px-3 py-2 w-full" rows="4" />')
            elif is_computed(field):
                lines.append(f'                    <input value={{data.{field_name}}} readOnly className="border rounded px-3 py-2 w-full bg-gray-100" />')
            else:
                value_type = field_type(field)
                input_type = 'number' if value_type in ('float', 'integer') else ('date' if value_type == 'date' else ('datetime-local' if value_type == 'datetime' else 'text'))
                required = 'true' if field['required'] else 'false'
                lines.append(f'                    <input type="{input_type}" value={{data.{field_name}}} readOnly={{readonly}} required={{{required}}} onChange={{(e) => setData(\'{field_name}\', e.target.value)}} className="border rounded px-3 py-2 w-full" />')

            lines.append('                </div>')

        lines += [
            '',
            '                {!readonly && (',
            '                    <button type="submit" disabled={processing} className="px-5 py-2 bg-blue-600 text-white rounded">',
            "                        {isEdit ? 'Update' : 'Save'}",
            '                    </button>',
            '                )}',
            '            </form>',
            '        </div>',
            '    );',
            '}',
            '',
        ]
        self.write(path, '\n'.join(lines))

    # ========================================================
    # ROUTES GENERATION
    # ========================================================

    def generate_routes(self):
        path = os.path.join(self.project, 'routes', 'generated.php')
        lines = ['<?php', '', 'use Illuminate\\Support\\Facades\\Route;', '']

        for model in self.models:
            class_name = pascal_case(model['name'])
            lines.append(f"use App\\Http\\Controllers\\{class_name}Controller;")

        lines.append('')

        for model in self.models:
            class_name = pascal_case(model['name'])
            url = model['url'].strip('/')
            route_name = snake_case(model['name'])
            lines.append(f"Route::resource('{url}', {class_name}Controller::class)->names('{route_name}')->parameters(['{url}' => 'record']);")

        lines.append('')
        self.write(path, '\n'.join(lines))

        web_path = os.path.join(self.project, 'routes', 'web.php')
        marker = '// DSL_GENERATED_ROUTES'
        require_line = "require base_path('routes/generated.php');"

        if os.path.exists(web_path):
            with open(web_path, 'r', encoding='utf-8') as file:
                content = file.read()
        else:
            content = '<?php\n'

        if marker not in content:
            content = content.rstrip() + '\n\n' + marker + '\n' + require_line + '\n'
            self.write(web_path, content)
        else:
            print('routes/web.php already contains DSL_GENERATED_ROUTES')

    # ========================================================
    # PRINT UTILITIES
    # ========================================================

    def print_routes(self):
        print('\n' + '=' * 80 + '\nGENERATED ROUTES\n' + '=' * 80)
        base_url = 'http://127.0.0.1:8000'
        print(f'Project path: {os.path.abspath(self.project)}')
        print(f'Test server:  cd "{os.path.abspath(self.project)}" && php artisan serve')
        for model in self.models:
            url = model['url']
            print(f"\n# {model['name']}")
            print('GET       ', base_url + url)
            print('GET       ', base_url + url + '/create')
            print('POST      ', base_url + url)
            print('GET       ', base_url + url + '/{record}')
            print('GET       ', base_url + url + '/{record}/edit')
            print('PUT/PATCH ', base_url + url + '/{record}')
            print('DELETE    ', base_url + url + '/{record}')

        print('\n' + '=' * 80 + '\nTEST COMMANDS\n' + '=' * 80)
        print('php artisan migrate')
        print('php artisan route:list')
        for model in self.models:
            print(f"php artisan route:list --path={model['url'].strip('/')}")

    def print_structure(self):
        print('\n' + '=' * 80 + '\nGENERATED FILES\n' + '=' * 80)
        for root, dirs, files in os.walk(self.project):
            dirs[:] = [d for d in dirs if d not in ('vendor', 'node_modules', '.git')]
            for filename in files:
                full_path = os.path.join(root, filename)
                relative = os.path.relpath(full_path, self.project)
                if relative.startswith(('app/', 'database/migrations/', 'resources/js/Pages/', 'routes/')):
                    print(os.path.abspath(full_path))

    def generate(self):
        if not self.project:
            raise ValueError('DSL must contain a project path (project: or project = "...")')
        if not self.module:
            raise ValueError('DSL must contain module:')
        if not self.models:
            raise ValueError('No models found in DSL')

        self.mkdir(self.project)
        directories = [
            os.path.join(self.project, 'app', 'Models'),
            os.path.join(self.project, 'app', 'Http', 'Controllers'),
            os.path.join(self.project, 'database', 'migrations'),
            os.path.join(self.project, 'resources', 'js', 'Pages', self.module),
            os.path.join(self.project, 'routes'),
        ]
        for d in directories:
            self.mkdir(d)

        for model in self.models:
            print('\nGenerating model:', model['name'])
            self.generate_model(model)

        for model in self.dependency_order():
            print('\nGenerating migration:', model['name'])
            self.generate_migration(model)

        for model in self.models:
            print('\nGenerating controller:', model['name'])
            self.generate_controller(model)
            print('Generating Index.jsx:', model['name'])
            self.generate_index(model)
            print('Generating Form.jsx:', model['name'])
            self.generate_form(model)

        self.generate_routes()
        self.print_routes()
        self.print_structure()
        print('\n' + '=' * 80 + '\nGENERATION COMPLETED\n' + '=' * 80)


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    data = parse_dsl(DSL)
    generator = Generator(data)
    generator.generate()