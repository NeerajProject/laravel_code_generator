import os
import re
from datetime import datetime, timedelta


# ============================================================
# DSL
# ============================================================

DSL = r'''
project = "/home/nj/workspace/laravel_code_generator/laravel_code_generator/laraval_caste/my_laravel_app"
module:Project

project.project
url:/projects

name:char*
manager_id:m2o(res.users)
start_date:date
end_date:date
state:selection(draft,in_progress,completed,cancelled)
description:text
task_ids:o2m(project.task)

list:
    name
    manager_id
    start_date
    state

filter:
    name
    manager_id
    state

form:
    name
    manager_id
    start_date
    end_date
    state
    description
    task_ids

menu:
    Project/Projects


project.task
url:/project-tasks

name:char*
project_id:m2o(project.project)
assignee_id:m2o(res.users)
deadline:date
state:selection(new,in_progress,review,done)
description:text
timesheet_ids:o2m(project.timesheet)
total_hours:float=compute_total_hours

list:
    name
    project_id
    assignee_id
    state
    deadline
    total_hours

filter:
    name
    project_id
    assignee_id
    state

form:
    name
    project_id
    assignee_id
    deadline
    state
    description
    timesheet_ids
    total_hours

compute:
    compute_total_hours:
        sum(timesheet_ids.hours)

menu:
    Project/Tasks


project.timesheet
url:/project-timesheets

date:date*
task_id:m2o(project.task)
employee_id:m2o(hr.employee)
description:char
hours:float*

list:
    date
    task_id
    employee_id
    hours
    description

filter:
    task_id
    employee_id
    date

form:
    date
    task_id
    employee_id
    hours
    description

menu:
    Project/Timesheets
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

    # --------------------------------------------------------
    # Paths
    # --------------------------------------------------------

    def module_dir(self):
        return os.path.join(self.project, 'app', 'Modules', pascal_case(self.module))

    def model_path(self, model):
        return os.path.join(self.module_dir(), 'Model', pascal_case(model['name']) + '.php')

    def controller_path(self, model):
        return os.path.join(self.module_dir(), 'Controller', pascal_case(model['name']) + 'Controller.php')

    def repository_path(self, model):
        name = pascal_case(model['name'])
        return os.path.join(self.module_dir(), 'Repository', name + 'Repository.php')

    def repository_interface_path(self, model):
        name = pascal_case(model['name'])
        return os.path.join(self.module_dir(), 'Repository', name + 'RepositoryInterface.php')

    def service_path(self, model):
        return os.path.join(self.module_dir(), 'Service', pascal_case(model['name']) + 'Service.php')

    def request_path(self, model):
        return os.path.join(self.module_dir(), 'Request', pascal_case(model['name']) + 'Request.php')

    def module_routes_path(self):
        return os.path.join(self.module_dir(), 'Routes', 'web.php')

    def page_dir(self, model):
        # Inertia renders '<Module>/<Model>/Index', which the default resolver
        # (./Pages/${name}.jsx) maps to resources/js/Pages/<Module>/<Model>/Index.jsx
        return os.path.join(
            self.project, 'resources', 'js', 'Pages',
            pascal_case(self.module), pascal_case(model['name'])
        )

    def migration_path(self, model):
        self.migration_index += 1
        table = table_name(model['name'])
        mig_dir = os.path.join(self.module_dir(), 'Database', 'Migrations')

        # Remove older generated migrations for this table so re-running the
        # generator doesn't cause "table already exists" on migrate.
        if os.path.isdir(mig_dir):
            for filename in os.listdir(mig_dir):
                if filename.endswith(f'_create_{table}_table.php'):
                    os.remove(os.path.join(mig_dir, filename))

        timestamp = datetime.now() + timedelta(seconds=self.migration_index)
        prefix = timestamp.strftime('%Y_%m_%d_%H%M%S')
        return os.path.join(mig_dir, f"{prefix}_create_{table}_table.php")

    # --------------------------------------------------------
    # Relation helpers
    # --------------------------------------------------------

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
        """m2o fields that need dropdown data on the form.

        Includes the model's own m2o fields plus the m2o fields of o2m child
        lines, except the inverse FK pointing back to this model (that one is
        set automatically and never shown as a dropdown).
        """
        fields = []
        for field in model['fields'].values():
            if is_m2o(field):
                fields.append(field)
            elif is_o2m(field):
                child = self.model_map[relation_model(field)]
                inverse = self.inverse_fk(model['name'], child)
                for child_field in child['fields'].values():
                    if (is_m2o(child_field)
                            and child_field['name'] in child['form']
                            and foreign_key_col(child_field['name']) != inverse):
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
            f'namespace App\\Modules\\{pascal_case(self.module)}\\Model;',
            '',
            'use Illuminate\\Database\\Eloquent\\Model;',
            'use Illuminate\\Database\\Eloquent\\Relations\\BelongsTo;',
            'use Illuminate\\Database\\Eloquent\\Relations\\HasMany;',
            '',
        ]
        imported = set()
        for field in model['fields'].values():
            if is_m2o(field) or is_o2m(field):
                target_name = pascal_case(relation_model(field))
                # Same namespace, so never import the class itself
                if target_name != class_name and target_name not in imported:
                    lines.append(
                        f'use App\\Modules\\{pascal_case(self.module)}\\Model\\{target_name};'
                    )
                    imported.add(target_name)
        lines += [
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
                casts.append(f"        '{field['name']}' => '{cast}',")

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

    def generate_repository(self, model):
        name = pascal_case(model['name'])
        namespace = f'App\\Modules\\{pascal_case(self.module)}'
        fields = [field['name'] for field in model['fields'].values()
                  if not is_o2m(field) and not is_computed(field)]
        searchable = [field['name'] for field in model['fields'].values()
                      if field_type(field) in ('char', 'text')]
        lines = [
            '<?php', '', f'namespace {namespace}\\Repository;', '',
            f'use {namespace}\\Model\\{name};', '',
            f'class {name}Repository implements {name}RepositoryInterface',
            '{',
            f'    public function __construct(protected {name} $model) {{}}', '',
            '    public function all(array $filters = [], array $with = [])',
            '    {',
            '        $query = $this->model->newQuery()->with($with);',
            '        foreach ($filters as $field => $value) {',
            "            if ($field === 'search' && $value !== null && $value !== '') {",
            '                $query->where(function ($q) use ($value) {',
        ]
        for index, field_name in enumerate(searchable):
            method = 'where' if index == 0 else 'orWhere'
            lines.append(
                f"                    $q->{method}('{field_name}', 'like', '%' . $value . '%');"
            )
        if not searchable:
            lines.append('                    $q->whereKey(0);')
        lines += [
            '                });',
            '                continue;',
            '            }',
            f"            if (in_array($field, {repr(fields)}, true) && $value !== null && $value !== '') {{",
            '                $query->where($field, $value);',
            '            }',
            '        }',
            '        return $query->latest()->paginate(20)->withQueryString();',
            '    }', '',
            '    public function find($id, array $with = [])',
            '    {',
            '        return $this->model->with($with)->findOrFail($id);',
            '    }', '',
            '    public function create(array $data) { return $this->model->create($data); }', '',
            '    public function update($id, array $data)',
            '    {',
            '        $record = $this->find($id);',
            '        $record->update($data);',
            '        return $record;',
            '    }', '',
            '    public function delete($id) { return $this->find($id)->delete(); }',
            '}',
            '',
        ]
        self.write(self.repository_path(model), '\n'.join(lines))

        interface_lines = [
            '<?php', '', f'namespace {namespace}\\Repository;', '',
            f'interface {name}RepositoryInterface',
            '{',
            '    public function all(array $filters = [], array $with = []);',
            '    public function find($id, array $with = []);',
            '    public function create(array $data);',
            '    public function update($id, array $data);',
            '    public function delete($id);',
            '}',
            '',
        ]
        self.write(self.repository_interface_path(model), '\n'.join(interface_lines))

    def generate_service(self, model):
        name = pascal_case(model['name'])
        namespace = f'App\\Modules\\{pascal_case(self.module)}'
        lines = [
            '<?php', '', f'namespace {namespace}\\Service;', '',
            f'use {namespace}\\Repository\\{name}RepositoryInterface;', '',
            f'class {name}Service',
            '{',
            f'    public function __construct(protected {name}RepositoryInterface $repository) {{}}',
            '',
            '    public function create(array $data) { return $this->repository->create($data); }',
            '    public function update($id, array $data) { return $this->repository->update($id, $data); }',
            '    public function delete($id) { return $this->repository->delete($id); }',
            '}',
            '',
        ]
        self.write(self.service_path(model), '\n'.join(lines))

    def generate_request(self, model):
        name = pascal_case(model['name'])
        namespace = f'App\\Modules\\{pascal_case(self.module)}'
        lines = [
            '<?php', '', f'namespace {namespace}\\Request;', '',
            'use Illuminate\\Foundation\\Http\\FormRequest;', '',
            f'class {name}Request extends FormRequest',
            '{',
            '    public function authorize(): bool { return true; }', '',
            '    public function rules(): array',
            '    {',
            '        return [',
        ]
        for field in model['fields'].values():
            if is_o2m(field) or is_computed(field):
                continue
            rule = 'required' if field['required'] else 'nullable'
            lines.append(f"            '{field['name']}' => '{rule}',")
        lines += ['        ];', '    }', '}', '']
        self.write(self.request_path(model), '\n'.join(lines))

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
        module_namespace = f'App\\Modules\\{pascal_case(self.module)}'
        imports = [
            'use Illuminate\\Http\\Request;',
            'use Illuminate\\Support\\Facades\\DB;',
            'use Inertia\\Inertia;',
            f"use {module_namespace}\\Model\\{class_name};",
            f"use {module_namespace}\\Repository\\{class_name}RepositoryInterface;",
            f"use {module_namespace}\\Service\\{class_name}Service;",
            f"use {module_namespace}\\Request\\{class_name}Request;",
        ]

        imported = {class_name}
        for field in self.relation_data_fields(model):
            target = pascal_case(relation_model(field))
            if target not in imported:
                imports.append(f"use {module_namespace}\\Model\\{target};")
                imported.add(target)

        lines = [
            '<?php',
            '',
            f'namespace {module_namespace}\\Controller;',
            '',
            *imports,
            '',
            'use App\\Http\\Controllers\\Controller;',
            '',
            f"class {class_name}Controller extends Controller",
            '{',
            f'    public function __construct(',
            f'        protected {class_name}RepositoryInterface $repository,',
            f'        protected {class_name}Service $service',
            '    ) {}',
            '',
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
            f"        return Inertia::render('{self.module}/{class_name}/Index', [",
            "            'records' => $records,",
            "            'filters' => $request->only('search'),",
            '        ]);',
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
            f'    public function store({class_name}Request $request)',
            '    {',
            "        return DB::transaction(function () use ($request) {",
            "            $data = $request->except(['_token']);",
        ]

        for field in model['fields'].values():
            if is_o2m(field) or is_computed(field):
                lines.append(f"            unset($data['{field['name']}']);")

        lines.append("            $record = $this->service->create($data);")
        lines += self.o2m_save_lines(model, '$record', '            ')
        lines += self.parent_compute_lines(model, '$record', '            ')

        route_name = model['name']
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
            f"    public function update({class_name}Request $request, {class_name} $record)",
            '    {',
            "        return DB::transaction(function () use ($request, $record) {",
            "            $data = $request->except(['_token', '_method']);",
        ]

        for field in model['fields'].values():
            if is_o2m(field) or is_computed(field):
                lines.append(f"            unset($data['{field['name']}']);")

        lines.append("            $record = $this->service->update($record->id, $data);")

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
            '        $this->service->delete($record->id);',
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
        title = label(model['name'])
        col_count = len(model['list']) + 1

        lines = []
        add = lines.append

        add("import React, { useState } from 'react';")
        add("import { Head, Link, router } from '@inertiajs/react';")
        add('')
        add('export default function Index({ records, filters = {} }) {')
        add("    const [search, setSearch] = useState(filters.search || '');")
        add('')
        add('    const submitSearch = (e) => {')
        add('        e.preventDefault();')
        add(f"        router.get('{url}', {{ search }}, {{ preserveState: true, replace: true }});")
        add('    };')
        add('')
        add('    const remove = (id) => {')
        add("        if (!confirm('Delete this record?')) return;")
        add(f"        router.delete(`{url}/${{id}}`);")
        add('    };')
        add('')
        add('    return (')
        add('        <div className="min-h-screen bg-slate-50">')
        add(f'            <Head title="{title}" />')
        add('')
        add('            {/* Page Header */}')
        add('            <div className="bg-white border-b border-slate-200">')
        add('                <div className="max-w-7xl mx-auto px-6 py-5">')
        add('                    <div className="flex items-center justify-between flex-wrap gap-3">')
        add('                        <div>')
        add('                            <nav className="text-xs text-slate-500 mb-1">')
        add(f'                                <span>Home</span>')
        add('                                <span className="mx-1.5">/</span>')
        add(f'                                <span className="text-slate-700 font-medium">{title}</span>')
        add('                            </nav>')
        add(f'                            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">{title}</h1>')
        add('                        </div>')
        add('                        <div className="flex items-center gap-2">')
        add('                            <button type="button" className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">')
        add('                                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" /></svg>')
        add('                                Filter')
        add('                            </button>')
        add('                            <button type="button" className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">')
        add('                                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>')
        add('                                Export')
        add('                            </button>')
        add(f'                            <Link href="{url}/create" className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40 transition">')
        add('                                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>')
        add('                                New Record')
        add('                            </Link>')
        add('                        </div>')
        add('                    </div>')
        add('                </div>')
        add('            </div>')
        add('')
        add('            <div className="max-w-7xl mx-auto px-6 py-6">')
        add('                <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">')
        add('')
        add('                    {/* Toolbar */}')
        add('                    <div className="px-5 py-3 border-b border-slate-200 flex items-center justify-between gap-3 flex-wrap">')
        add('                        <form onSubmit={submitSearch} className="relative flex-1 max-w-md">')
        add('                            <svg className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">')
        add('                                <circle cx="11" cy="11" r="7" />')
        add('                                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35" />')
        add('                            </svg>')
        add('                            <input')
        add('                                value={search}')
        add('                                onChange={(e) => setSearch(e.target.value)}')
        add('                                placeholder="Search records..."')
        add('                                className="w-full pl-9 pr-3 py-2 text-sm bg-white border border-slate-300 rounded-md placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 transition"')
        add('                            />')
        add('                        </form>')
        add('                        <div className="text-xs text-slate-500">')
        add('                            {records.total !== undefined ? `${records.total} record${records.total !== 1 ? \'s\' : \'\'}` : \'\'}')
        add('                        </div>')
        add('                    </div>')
        add('')
        add('                    {/* Table */}')
        add('                    <div className="overflow-x-auto">')
        add('                        <table className="w-full text-sm">')
        add('                            <thead>')
        add('                                <tr className="bg-slate-50 border-b border-slate-200">')
        add('                                    <th className="w-10 px-4 py-3">')
        add('                                        <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />')
        add('                                    </th>')

        for field_name in model['list']:
            add(f'                                    <th className="px-5 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">{label(field_name)}</th>')

        add('                                    <th className="px-5 py-3 text-right text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">Actions</th>')
        add('                                </tr>')
        add('                            </thead>')
        add('                            <tbody className="divide-y divide-slate-100">')
        add('                                {records.data.length === 0 && (')
        add('                                    <tr>')
        add(f'                                        <td colSpan={{{col_count + 1}}} className="px-6 py-16 text-center">')
        add('                                            <div className="flex flex-col items-center gap-2 text-slate-400">')
        add('                                                <svg className="w-12 h-12" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">')
        add('                                                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />')
        add('                                                </svg>')
        add('                                                <p className="text-sm font-medium">No records found</p>')
        add('                                                <p className="text-xs">Try adjusting your search or create a new record.</p>')
        add('                                            </div>')
        add('                                        </td>')
        add('                                    </tr>')
        add('                                )}')
        add('                                {records.data.map((row) => (')
        add('                                    <tr key={row.id} className="hover:bg-slate-50/70 transition-colors">')
        add('                                        <td className="px-4 py-3">')
        add('                                            <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />')
        add('                                        </td>')

        for field_name in model['list']:
            field = model['fields'].get(field_name)
            add('                                        <td className="px-5 py-3 text-slate-700 whitespace-nowrap">')

            if field and is_m2o(field):
                rel = relation_method_name(field_name)
                add(f'                                            {{row.{rel}?.name || row.{field_name} || \'-\'}}')
            elif field and is_selection(field):
                add(f'                                            {{row.{field_name} ? (')
                add(f'                                                <span className={{')
                add(f'                                                    \'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium \' +')
                add(f"                                                    (row.{field_name} === 'confirmed' ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200' :")
                add(f"                                                     row.{field_name} === 'cancelled' ? 'bg-rose-50 text-rose-700 ring-1 ring-rose-200' :")
                add(f"                                                     'bg-slate-100 text-slate-700 ring-1 ring-slate-200')")
                add('                                                }>')
                add(f'                                                    {{row.{field_name}}}')
                add('                                                </span>')
                add('                                            ) : \'-\'}')
            elif field and field_type(field) == 'bool':
                add(f'                                            {{row.{field_name} ? (')
                add('                                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200">Yes</span>')
                add('                                            ) : (')
                add('                                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 ring-1 ring-slate-200">No</span>')
                add('                                            )}')
            elif field and field_type(field) == 'float':
                add(f'                                            <span className="font-medium text-slate-900 tabular-nums">{{Number(row.{field_name} ?? 0).toFixed(2)}}</span>')
            else:
                add(f'                                            {{row.{field_name} ?? \'-\'}}')

            add('                                        </td>')

        add('                                        <td className="px-5 py-3 text-right whitespace-nowrap">')
        add('                                            <div className="inline-flex items-center gap-1">')
        add(f'                                                <Link href={{`{url}/${{row.id}}/edit`}} className="inline-flex items-center justify-center w-8 h-8 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-md transition" title="Edit">')
        add('                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>')
        add('                                                </Link>')
        add('                                                <button onClick={() => remove(row.id)} className="inline-flex items-center justify-center w-8 h-8 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-md transition" title="Delete">')
        add('                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M9 7V4a1 1 0 011-1h4a1 1 0 011 1v3" /></svg>')
        add('                                                </button>')
        add('                                            </div>')
        add('                                        </td>')
        add('                                    </tr>')
        add('                                ))}')
        add('                            </tbody>')
        add('                        </table>')
        add('                    </div>')
        add('')
        add('                    {/* Pagination */}')
        add('                    {records.links && records.links.length > 3 && (')
        add('                        <div className="px-5 py-3 border-t border-slate-200 flex items-center justify-between gap-3 flex-wrap bg-slate-50/40">')
        add('                            <div className="text-xs text-slate-500">')
        add('                                Showing <span className="font-medium text-slate-700">{records.from ?? 0}</span> to <span className="font-medium text-slate-700">{records.to ?? 0}</span> of <span className="font-medium text-slate-700">{records.total}</span> entries')
        add('                            </div>')
        add('                            <div className="flex items-center gap-1">')
        add('                                {records.links.map((link, i) => (')
        add('                                    <button')
        add('                                        key={i}')
        add('                                        disabled={!link.url}')
        add('                                        onClick={() => link.url && router.get(link.url, {}, { preserveState: true })}')
        add('                                        dangerouslySetInnerHTML={{ __html: link.label }}')
        add("                                        className={`min-w-[32px] h-8 px-2 text-xs font-medium rounded-md border transition ${link.active ? 'bg-blue-600 text-white border-blue-600 shadow-sm' : 'bg-white text-slate-600 border-slate-300 hover:bg-slate-100'} ${!link.url ? 'opacity-40 cursor-not-allowed' : ''}`}")
        add('                                    />')
        add('                                ))}')
        add('                            </div>')
        add('                        </div>')
        add('                    )}')
        add('                </div>')
        add('            </div>')
        add('        </div>')
        add('    );')
        add('}')
        add('')

        self.write(path, '\n'.join(lines))

    # ========================================================
    # INERTIA FORM REACT COMPONENT
    # ========================================================

    def generate_form(self, model):
        path = os.path.join(self.page_dir(model), 'Form.jsx')
        url = model['url']
        title = label(model['name'])

        lines = []
        add = lines.append

        add("import React from 'react';")
        add("import { Head, Link, useForm } from '@inertiajs/react';")
        add('')
        add('export default function Form({ record, relations = {}, readonly = false }) {')
        add('    const isEdit = !!record?.id;')
        add('')
        add('    const { data, setData, post, put, processing, errors } = useForm({')

        for field_name in model['form']:
            field = model['fields'].get(field_name)
            if not field:
                continue
            if is_o2m(field):
                add(f"        {field_name}: record?.{field_name} || [],")
            elif is_m2o(field):
                rel = relation_method_name(field_name)
                add(f"        {field_name}: record?.{field_name} ?? record?.{rel}?.id ?? '',")
            elif field_type(field) == 'bool':
                add(f"        {field_name}: record?.{field_name} ?? false,")
            else:
                add(f"        {field_name}: record?.{field_name} ?? '',")

        add('    });')
        add('')
        add('    const submit = (e) => {')
        add('        e.preventDefault();')
        add('        if (isEdit) {')
        add(f"            put(`{url}/${{record.id}}`);")
        add('        } else {')
        add(f"            post('{url}');")
        add('        }')
        add('    };')

        # o2m helpers
        for field in model['fields'].values():
            if not is_o2m(field):
                continue
            relation = field['name']
            child = self.model_map[relation_model(field)]
            add_fn = 'add' + pascal_case(relation)
            remove_fn = 'remove' + pascal_case(relation)
            update_fn = 'update' + pascal_case(relation)

            add('')
            add(f'    const {add_fn} = () => {{')
            add(f"        setData('{relation}', [")
            add(f"            ...(data.{relation} || []),")
            add('            {')
            for child_name in child['form']:
                child_field = child['fields'].get(child_name)
                if child_field and not is_computed(child_field):
                    add(f"                {child_name}: '',")
            add('            },')
            add('        ]);')
            add('    };')

            add('')
            add(f'    const {remove_fn} = (index) => {{')
            add(f"        setData('{relation}', (data.{relation} || []).filter((_, i) => i !== index));")
            add('    };')

            add('')
            add(f'    const {update_fn} = (index, key, value) => {{')
            add(f"        const copy = [...(data.{relation} || [])];")
            add('        copy[index] = { ...copy[index], [key]: value };')
            add(f"        setData('{relation}', copy);")
            add('    };')

        add('')
        add('    return (')
        add('        <div className="min-h-screen bg-slate-50">')
        add(f'            <Head title="{title}" />')
        add('')
        add('            {/* Page Header */}')
        add('            <div className="bg-white border-b border-slate-200">')
        add('                <div className="max-w-5xl mx-auto px-6 py-5">')
        add('                    <div className="flex items-center justify-between flex-wrap gap-3">')
        add('                        <div>')
        add('                            <nav className="text-xs text-slate-500 mb-1">')
        add(f'                                <Link href="{url}" className="hover:text-slate-700">Home</Link>')
        add('                                <span className="mx-1.5">/</span>')
        add(f'                                <Link href="{url}" className="hover:text-slate-700">{title}</Link>')
        add('                                <span className="mx-1.5">/</span>')
        add("                                <span className=\"text-slate-700 font-medium\">{isEdit ? 'Edit' : 'New'}</span>")
        add('                            </nav>')
        add('                            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">')
        add("                                {isEdit ? 'Edit' : 'New'} " + title)
        add('                            </h1>')
        add('                        </div>')
        add(f'                        <Link href="{url}" className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">')
        add('                            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>')
        add('                            Back')
        add('                        </Link>')
        add('                    </div>')
        add('                </div>')
        add('            </div>')
        add('')
        add('            <form onSubmit={submit} className="max-w-5xl mx-auto px-6 py-6 space-y-6">')

        # Scalar fields card
        scalar_fields = []
        o2m_fields = []
        for field_name in model['form']:
            field = model['fields'].get(field_name)
            if not field:
                continue
            if is_o2m(field):
                o2m_fields.append(field)
            else:
                scalar_fields.append(field)

        if scalar_fields:
            add('                {/* Details Section */}')
            add('                <div className="bg-white rounded-lg shadow-sm border border-slate-200">')
            add('                    <div className="px-6 py-4 border-b border-slate-200 flex items-center gap-3">')
            add('                        <div className="w-8 h-8 rounded-md bg-blue-50 flex items-center justify-center">')
            add('                            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>')
            add('                        </div>')
            add('                        <div>')
            add('                            <h2 className="text-sm font-semibold text-slate-800">Details</h2>')
            add('                            <p className="text-xs text-slate-500">Basic information about this record</p>')
            add('                        </div>')
            add('                    </div>')
            add('                    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-x-5 gap-y-5">')

            input_cls = (
                "w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md "
                "px-3 py-2 placeholder:text-slate-400 transition "
                "focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 "
                "disabled:bg-slate-50 disabled:text-slate-500 read-only:bg-slate-50"
            )

            for field in scalar_fields:
                field_name = field['name']
                required_mark = ' <span className="text-rose-500">*</span>' if field['required'] else ''
                add('')
                add('                        <div>')
                add(f'                            <label className="block text-xs font-semibold text-slate-700 mb-1.5">{label(field_name)}{required_mark}</label>')

                if is_m2o(field):
                    add(f'                            <select value={{data.{field_name}}} disabled={{readonly}} onChange={{(e) => setData(\'{field_name}\', e.target.value)}} className="{input_cls}">')
                    add('                                <option value="">Select...</option>')
                    add(f"                                {{(relations['{field_name}'] || []).map((item) => (")
                    add('                                    <option key={item.id} value={item.id}>{item.name}</option>')
                    add('                                ))}')
                    add('                            </select>')
                elif is_selection(field):
                    add(f'                            <select value={{data.{field_name}}} disabled={{readonly}} onChange={{(e) => setData(\'{field_name}\', e.target.value)}} className="{input_cls}">')
                    add('                                <option value="">Select...</option>')
                    for val in selection_values(field):
                        add(f'                                <option value="{val}">{label(val)}</option>')
                    add('                            </select>')
                elif field_type(field) == 'bool':
                    add('                            <label className="inline-flex items-center gap-2 cursor-pointer select-none pt-1">')
                    add(f'                                <input type="checkbox" checked={{!!data.{field_name}}} disabled={{readonly}} onChange={{(e) => setData(\'{field_name}\', e.target.checked)}} className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />')
                    add('                                <span className="text-sm text-slate-700">Yes</span>')
                    add('                            </label>')
                elif field_type(field) == 'text':
                    add(f'                            <textarea value={{data.{field_name}}} readOnly={{readonly}} onChange={{(e) => setData(\'{field_name}\', e.target.value)}} rows="4" className="{input_cls}" />')
                elif is_computed(field):
                    add(f'                            <input value={{data.{field_name}}} readOnly className="w-full text-sm font-medium text-slate-800 bg-slate-50 border border-slate-200 rounded-md px-3 py-2" />')
                else:
                    value_type = field_type(field)
                    input_type = 'number' if value_type in ('float', 'integer') else (
                        'date' if value_type == 'date' else (
                            'datetime-local' if value_type == 'datetime' else 'text'
                        )
                    )
                    step = 'step="0.01"' if value_type == 'float' else ''
                    required_attr = 'required' if field['required'] else ''
                    add(f'                            <input type="{input_type}" {step} {required_attr} value={{data.{field_name}}} readOnly={{readonly}} onChange={{(e) => setData(\'{field_name}\', e.target.value)}} className="{input_cls}" />')

                add(f"                            {{errors.{field_name} && <p className=\"mt-1 text-xs text-rose-600\">{{errors.{field_name}}}</p>}}")
                add('                        </div>')

            add('                    </div>')
            add('                </div>')

        # o2m line-item cards
        for field in o2m_fields:
            field_name = field['name']
            child = self.model_map[relation_model(field)]
            add_fn = 'add' + pascal_case(field_name)
            remove_fn = 'remove' + pascal_case(field_name)
            update_fn = 'update' + pascal_case(field_name)

            visible_child_cols = [c for c in child['form'] if child['fields'].get(c)]
            col_span = len(visible_child_cols) + 1

            cell_cls = (
                "w-full text-sm text-slate-800 bg-white border border-slate-300 rounded-md "
                "px-2.5 py-1.5 placeholder:text-slate-400 transition "
                "focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 "
                "disabled:bg-slate-50 disabled:text-slate-500"
            )

            add('')
            add('                {/* Line Items */}')
            add('                <div className="bg-white rounded-lg shadow-sm border border-slate-200">')
            add('                    <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between gap-3">')
            add('                        <div className="flex items-center gap-3">')
            add('                            <div className="w-8 h-8 rounded-md bg-indigo-50 flex items-center justify-center">')
            add('                                <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" /></svg>')
            add('                            </div>')
            add('                            <div>')
            add(f'                                <h2 className="text-sm font-semibold text-slate-800">{label(field_name)}</h2>')
            add('                                <p className="text-xs text-slate-500">Add one or more line items</p>')
            add('                            </div>')
            add('                        </div>')
            add(f'                        {{!readonly && (')
            add(f'                            <button type="button" onClick={{{add_fn}}} className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-md transition">')
            add('                                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>')
            add('                                Add Line')
            add('                            </button>')
            add('                        )}')
            add('                    </div>')
            add('                    <div className="overflow-x-auto">')
            add('                        <table className="w-full text-sm">')
            add('                            <thead>')
            add('                                <tr className="bg-slate-50 border-b border-slate-200">')
            for child_name in visible_child_cols:
                add(f'                                    <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap">{label(child_name)}</th>')
            add('                                    <th className="w-14 px-3 py-2.5"></th>')
            add('                                </tr>')
            add('                            </thead>')
            add('                            <tbody className="divide-y divide-slate-100">')
            add(f'                                {{(data.{field_name} || []).length === 0 ? (')
            add('                                    <tr>')
            add(f'                                        <td colSpan={{{col_span}}} className="px-6 py-10 text-center">')
            add('                                            <div className="flex flex-col items-center gap-2 text-slate-400">')
            add('                                                <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>')
            add('                                                <p className="text-xs">No lines added yet. Click "Add Line" to begin.</p>')
            add('                                            </div>')
            add('                                        </td>')
            add('                                    </tr>')
            add(f'                                ) : (data.{field_name} || []).map((line, index) => (')
            add('                                    <tr key={index} className="hover:bg-slate-50/60">')

            for child_name in visible_child_cols:
                child_field = child['fields'][child_name]
                add('                                        <td className="px-4 py-2.5 align-top">')

                if is_m2o(child_field):
                    add(f'                                            <select value={{line.{child_name} ?? \'\'}} disabled={{readonly}} onChange={{(e) => {update_fn}(index, \'{child_name}\', e.target.value)}} className="{cell_cls}">')
                    add('                                                <option value="">Select...</option>')
                    add(f"                                                {{(relations['{child_name}'] || []).map((item) => (")
                    add('                                                    <option key={item.id} value={item.id}>{item.name}</option>')
                    add('                                                ))}')
                    add('                                            </select>')
                elif is_computed(child_field):
                    add(f'                                            <input value={{line.{child_name} ?? \'\'}} readOnly className="w-full text-sm font-medium text-slate-800 bg-slate-50 border border-slate-200 rounded-md px-2.5 py-1.5" />')
                else:
                    child_type = field_type(child_field)
                    input_type = 'number' if child_type in ('float', 'integer') else (
                        'date' if child_type == 'date' else 'text'
                    )
                    step = 'step="0.01"' if child_type == 'float' else ''
                    add(f'                                            <input type="{input_type}" {step} value={{line.{child_name} ?? \'\'}} disabled={{readonly}} onChange={{(e) => {update_fn}(index, \'{child_name}\', e.target.value)}} className="{cell_cls}" />')

                add('                                        </td>')

            add('                                        <td className="px-3 py-2.5 text-center align-middle">')
            add('                                            {!readonly && (')
            add(f'                                                <button type="button" onClick={{() => {remove_fn}(index)}} className="inline-flex items-center justify-center w-8 h-8 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-md transition" title="Remove">')
            add('                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M9 7V4a1 1 0 011-1h4a1 1 0 011 1v3" /></svg>')
            add('                                                </button>')
            add('                                            )}')
            add('                                        </td>')
            add('                                    </tr>')
            add('                                ))}')
            add('                            </tbody>')
            add('                        </table>')
            add('                    </div>')
            add('                </div>')

        # Footer actions
        add('')
        add('                {/* Actions */}')
        add('                {!readonly && (')
        add('                    <div className="bg-white rounded-lg shadow-sm border border-slate-200 px-6 py-4 flex items-center justify-between flex-wrap gap-3 sticky bottom-4">')
        add('                        <p className="text-xs text-slate-500">')
        add('                            Fields marked <span className="text-rose-500">*</span> are required')
        add('                        </p>')
        add('                        <div className="flex items-center gap-2">')
        add(f'                            <Link href="{url}" className="inline-flex items-center px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition">Cancel</Link>')
        add('                            <button type="submit" disabled={processing} className="inline-flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white bg-blue-600 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40 disabled:opacity-60 disabled:cursor-not-allowed transition">')
        add('                                {processing && (')
        add('                                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg>')
        add('                                )}')
        add("                                {isEdit ? 'Update' : 'Save'}")
        add('                            </button>')
        add('                        </div>')
        add('                    </div>')
        add('                )}')
        add('            </form>')
        add('        </div>')
        add('    );')
        add('}')
        add('')

        self.write(path, '\n'.join(lines))

    # ========================================================
    # ROUTES GENERATION
    # ========================================================

    def generate_routes(self):
        path = self.module_routes_path()
        lines = ['<?php', '', 'use Illuminate\\Support\\Facades\\Route;', '']

        for model in self.models:
            class_name = pascal_case(model['name'])
            lines.append(
                f"use App\\Modules\\{pascal_case(self.module)}\\Controller\\{class_name}Controller;"
            )

        lines.append('')

        for model in self.models:
            class_name = pascal_case(model['name'])
            url = model['url'].strip('/')
            route_name = model['name']
            lines.append(
                f"Route::resource('{url}', {class_name}Controller::class)->names('{route_name}')->parameters(['{url}' => 'record']);"
            )

        lines.append('')
        self.write(path, '\n'.join(lines))

        web_path = os.path.join(self.project, 'routes', 'web.php')
        marker = '// DSL_GENERATED_ROUTES'
        require_line = (
            f"require app_path('Modules/{pascal_case(self.module)}/Routes/web.php');"
        )

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
        module_pages = os.path.join('resources', 'js', 'Pages', pascal_case(self.module)) + os.sep
        for root, dirs, files in os.walk(self.project):
            dirs[:] = [d for d in dirs if d not in ('vendor', 'node_modules', '.git')]
            for filename in files:
                full_path = os.path.join(root, filename)
                relative = os.path.relpath(full_path, self.project)
                if relative.startswith(('app/Modules/', 'routes/', module_pages)):
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
            os.path.join(self.module_dir(), 'Model'),
            os.path.join(self.module_dir(), 'Repository'),
            os.path.join(self.module_dir(), 'Service'),
            os.path.join(self.module_dir(), 'Request'),
            os.path.join(self.module_dir(), 'Controller'),
            os.path.join(self.module_dir(), 'Database', 'Migrations'),
            os.path.join(self.module_dir(), 'Routes'),
            os.path.join(self.project, 'routes'),
            os.path.join(self.project, 'resources', 'js', 'Pages', pascal_case(self.module)),
        ]
        for d in directories:
            self.mkdir(d)

        for model in self.models:
            print('\nGenerating model:', model['name'])
            self.generate_model(model)
            self.generate_repository(model)
            self.generate_service(model)
            self.generate_request(model)

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
