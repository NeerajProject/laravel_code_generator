<?php

namespace App\Modules\Project\Controller;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;
use App\Modules\Project\Model\ProjectTask;
use App\Modules\Project\Repository\ProjectTaskRepositoryInterface;
use App\Modules\Project\Service\ProjectTaskService;
use App\Modules\Project\Request\ProjectTaskRequest;
use App\Modules\Project\Model\ProjectProject;
use App\Modules\Project\Model\ResUsers;
use App\Modules\Project\Model\HrEmployee;

use App\Http\Controllers\Controller;

class ProjectTaskController extends Controller
{
    public function __construct(
        protected ProjectTaskRepositoryInterface $repository,
        protected ProjectTaskService $service
    ) {}

    public function index(Request $request)
    {
        $query = ProjectTask::query();
        $query->with(['project', 'assignee', 'timesheet_ids']);

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('name', 'like', '%' . $search . '%');
                $q->orWhere('description', 'like', '%' . $search . '%');
            });
        }

        $records = $query->latest()->paginate(20)->withQueryString();

        return Inertia::render('Project/ProjectTask/Index', [
            'records' => $records,
            'filters' => $request->only('search'),
        ]);
    }

    public function create()
    {
        return Inertia::render(
            'Project/ProjectTask/Form',
            [
                'record' => null,
                'relations' => $this->relationData(),
            ]
        );
    }

    public function store(ProjectTaskRequest $request)
    {
        return DB::transaction(function () use ($request) {
            $data = $request->except(['_token']);
            unset($data['timesheet_ids']);
            unset($data['total_hours']);
            $record = $this->service->create($data);

            foreach ($request->input('timesheet_ids', []) as $lineData) {
                $lineData['task_id'] = $record->id;
                ProjectTimesheet::create($lineData);
            }

            $record->update([
                'total_hours' => $record->timesheet_ids()->sum('hours'),
            ]);

            return redirect()->route('project.task.index')->with('success', 'Created successfully.');
        });
    }

    public function show(ProjectTask $record)
    {
        $record->load($this->relations());
        return Inertia::render('Project/ProjectTask/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
            'readonly' => true,
        ]);
    }

    public function edit(ProjectTask $record)
    {
        $record->load($this->relations());
        return Inertia::render('Project/ProjectTask/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
        ]);
    }

    public function update(ProjectTaskRequest $request, ProjectTask $record)
    {
        return DB::transaction(function () use ($request, $record) {
            $data = $request->except(['_token', '_method']);
            unset($data['timesheet_ids']);
            unset($data['total_hours']);
            $record = $this->service->update($record->id, $data);
            $record->timesheet_ids()->delete();

            foreach ($request->input('timesheet_ids', []) as $lineData) {
                $lineData['task_id'] = $record->id;
                ProjectTimesheet::create($lineData);
            }

            $record->update([
                'total_hours' => $record->timesheet_ids()->sum('hours'),
            ]);

            return redirect()->route('project.task.index')->with('success', 'Updated successfully.');
        });
    }

    public function destroy(ProjectTask $record)
    {
        $this->service->delete($record->id);
        return redirect()->back()->with('success', 'Deleted successfully.');
    }

    private function relations(): array
    {
        return ["project", "assignee", "timesheet_ids"];
    }

    private function relationData(): array
    {
        $relations = [];
        $relations['project_id'] = ProjectProject::orderBy('name')->get(['id', 'name']);
        $relations['assignee_id'] = ResUsers::orderBy('name')->get(['id', 'name']);
        $relations['employee_id'] = HrEmployee::orderBy('name')->get(['id', 'name']);
        return $relations;
    }
}
