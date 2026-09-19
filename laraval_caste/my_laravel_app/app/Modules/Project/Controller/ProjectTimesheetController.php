<?php

namespace App\Modules\Project\Controller;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;
use App\Modules\Project\Model\ProjectTimesheet;
use App\Modules\Project\Repository\ProjectTimesheetRepositoryInterface;
use App\Modules\Project\Service\ProjectTimesheetService;
use App\Modules\Project\Request\ProjectTimesheetRequest;
use App\Modules\Project\Model\ProjectTask;
use App\Modules\Project\Model\HrEmployee;

use App\Http\Controllers\Controller;

class ProjectTimesheetController extends Controller
{
    public function __construct(
        protected ProjectTimesheetRepositoryInterface $repository,
        protected ProjectTimesheetService $service
    ) {}

    public function index(Request $request)
    {
        $query = ProjectTimesheet::query();
        $query->with(['task', 'employee']);

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('description', 'like', '%' . $search . '%');
            });
        }

        $records = $query->latest()->paginate(20)->withQueryString();

        return Inertia::render('Project/ProjectTimesheet/Index', [
            'records' => $records,
            'filters' => $request->only('search'),
        ]);
    }

    public function create()
    {
        return Inertia::render(
            'Project/ProjectTimesheet/Form',
            [
                'record' => null,
                'relations' => $this->relationData(),
            ]
        );
    }

    public function store(ProjectTimesheetRequest $request)
    {
        return DB::transaction(function () use ($request) {
            $data = $request->except(['_token']);
            $record = $this->service->create($data);

            return redirect()->route('project.timesheet.index')->with('success', 'Created successfully.');
        });
    }

    public function show(ProjectTimesheet $record)
    {
        $record->load($this->relations());
        return Inertia::render('Project/ProjectTimesheet/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
            'readonly' => true,
        ]);
    }

    public function edit(ProjectTimesheet $record)
    {
        $record->load($this->relations());
        return Inertia::render('Project/ProjectTimesheet/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
        ]);
    }

    public function update(ProjectTimesheetRequest $request, ProjectTimesheet $record)
    {
        return DB::transaction(function () use ($request, $record) {
            $data = $request->except(['_token', '_method']);
            $record = $this->service->update($record->id, $data);

            return redirect()->route('project.timesheet.index')->with('success', 'Updated successfully.');
        });
    }

    public function destroy(ProjectTimesheet $record)
    {
        $this->service->delete($record->id);
        return redirect()->back()->with('success', 'Deleted successfully.');
    }

    private function relations(): array
    {
        return ["task", "employee"];
    }

    private function relationData(): array
    {
        $relations = [];
        $relations['task_id'] = ProjectTask::orderBy('name')->get(['id', 'name']);
        $relations['employee_id'] = HrEmployee::orderBy('name')->get(['id', 'name']);
        return $relations;
    }
}
