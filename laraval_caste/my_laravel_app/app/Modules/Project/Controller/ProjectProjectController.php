<?php

namespace App\Modules\Project\Controller;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use App\Modules\Project\Repository\ProjectProjectRepositoryInterface;
use App\Modules\Project\Service\ProjectProjectService;
use App\Modules\Project\Request\ProjectProjectRequest;

class ProjectProjectController extends Controller
{
    public function __construct(
        protected ProjectProjectRepositoryInterface $repository,
        protected ProjectProjectService $service
    ) {}

    public function index(Request $request)
    {
        $filters = $request->get('filters', []);
        if ($request->has('search') && !isset($filters['search'])) {
            $filters['search'] = $request->get('search');
        }

        return Inertia::render('Modules/Project/ProjectProject/Index', [
            'records' => $this->repository->all($filters),
            'filters' => $filters,
        ]);
    }

    public function create()
    {
        return Inertia::render('Modules/Project/ProjectProject/Form', [
            'record' => null,
            'lookups' => [],
        ]);
    }

    public function store(ProjectProjectRequest $request)
    {
        $this->repository->create($request->validated());
        return redirect()->route('project.project.index');
    }

    public function show($id)
    {
        return Inertia::render('Modules/Project/ProjectProject/Show', [
            'record' => $this->repository->find($id),
        ]);
    }

    public function edit($id)
    {
        return Inertia::render('Modules/Project/ProjectProject/Form', [
            'record' => $this->repository->find($id),
            'lookups' => [],
        ]);
    }

    public function update(ProjectProjectRequest $request, $id)
    {
        $this->repository->update($id, $request->validated());
        return redirect()->route('project.project.index');
    }

    public function destroy($id)
    {
        $this->repository->delete($id);
        return redirect()->route('project.project.index');
    }
}
