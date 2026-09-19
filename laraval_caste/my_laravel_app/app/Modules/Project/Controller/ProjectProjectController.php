<?php

namespace App\Modules\Project\Controller;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;
use App\Modules\Project\Model\ProjectProject;
use App\Modules\Project\Repository\ProjectProjectRepositoryInterface;
use App\Modules\Project\Service\ProjectProjectService;
use App\Modules\Project\Request\ProjectProjectRequest;
use App\Modules\Project\Model\ResUsers;

use App\Http\Controllers\Controller;

class ProjectProjectController extends Controller
{
    public function __construct(
        protected ProjectProjectRepositoryInterface $repository,
        protected ProjectProjectService $service
    ) {}

    public function index(Request $request)
    {
        $query = ProjectProject::query();
        $query->with(['manager', 'task_ids']);

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('name', 'like', '%' . $search . '%');
                $q->orWhere('description', 'like', '%' . $search . '%');
            });
        }

        $records = $query->latest()->paginate(20)->withQueryString();

        return Inertia::render('Project/ProjectProject/Index', [
            'records' => $records,
            'filters' => $request->only('search'),
        ]);
    }

    public function create()
    {
        return Inertia::render(
            'Project/ProjectProject/Form',
            [
                'record' => null,
                'relations' => $this->relationData(),
            ]
        );
    }

    public function store(ProjectProjectRequest $request)
    {
        return DB::transaction(function () use ($request) {
            $data = $request->except(['_token']);
            unset($data['task_ids']);
            $record = $this->service->create($data);

            foreach ($request->input('task_ids', []) as $lineData) {
                $lineData['project_id'] = $record->id;
                ProjectTask::create($lineData);
            }

            return redirect()->route('project.project.index')->with('success', 'Created successfully.');
        });
    }

    public function show(ProjectProject $record)
    {
        $record->load($this->relations());
        return Inertia::render('Project/ProjectProject/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
            'readonly' => true,
        ]);
    }

    public function edit(ProjectProject $record)
    {
        $record->load($this->relations());
        return Inertia::render('Project/ProjectProject/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
        ]);
    }

    public function update(ProjectProjectRequest $request, ProjectProject $record)
    {
        return DB::transaction(function () use ($request, $record) {
            $data = $request->except(['_token', '_method']);
            unset($data['task_ids']);
            $record = $this->service->update($record->id, $data);
            $record->task_ids()->delete();

            foreach ($request->input('task_ids', []) as $lineData) {
                $lineData['project_id'] = $record->id;
                ProjectTask::create($lineData);
            }

            return redirect()->route('project.project.index')->with('success', 'Updated successfully.');
        });
    }

    public function destroy(ProjectProject $record)
    {
        $this->service->delete($record->id);
        return redirect()->back()->with('success', 'Deleted successfully.');
    }

    private function relations(): array
    {
        return ["manager", "task_ids"];
    }

    private function relationData(): array
    {
        $relations = [];
        $relations['manager_id'] = ResUsers::orderBy('name')->get(['id', 'name']);
        $relations['assignee_id'] = ResUsers::orderBy('name')->get(['id', 'name']);
        return $relations;
    }
}
