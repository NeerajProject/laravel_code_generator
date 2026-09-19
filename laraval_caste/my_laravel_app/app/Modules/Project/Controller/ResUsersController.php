<?php

namespace App\Modules\Project\Controller;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;
use App\Modules\Project\Model\ResUsers;
use App\Modules\Project\Repository\ResUsersRepositoryInterface;
use App\Modules\Project\Service\ResUsersService;
use App\Modules\Project\Request\ResUsersRequest;

use App\Http\Controllers\Controller;

class ResUsersController extends Controller
{
    public function __construct(
        protected ResUsersRepositoryInterface $repository,
        protected ResUsersService $service
    ) {}

    public function index(Request $request)
    {
        $query = ResUsers::query();

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('name', 'like', '%' . $search . '%');
            });
        }

        $records = $query->latest()->paginate(20)->withQueryString();

        return Inertia::render('Project/ResUsers/Index', [
            'records' => $records,
            'filters' => $request->only('search'),
        ]);
    }

    public function create()
    {
        return Inertia::render(
            'Project/ResUsers/Form',
            [
                'record' => null,
                'relations' => $this->relationData(),
            ]
        );
    }

    public function store(ResUsersRequest $request)
    {
        return DB::transaction(function () use ($request) {
            $data = $request->except(['_token']);
            $record = $this->service->create($data);

            return redirect()->route('res.users.index')->with('success', 'Created successfully.');
        });
    }

    public function show(ResUsers $record)
    {
        $record->load($this->relations());
        return Inertia::render('Project/ResUsers/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
            'readonly' => true,
        ]);
    }

    public function edit(ResUsers $record)
    {
        $record->load($this->relations());
        return Inertia::render('Project/ResUsers/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
        ]);
    }

    public function update(ResUsersRequest $request, ResUsers $record)
    {
        return DB::transaction(function () use ($request, $record) {
            $data = $request->except(['_token', '_method']);
            $record = $this->service->update($record->id, $data);

            return redirect()->route('res.users.index')->with('success', 'Updated successfully.');
        });
    }

    public function destroy(ResUsers $record)
    {
        $this->service->delete($record->id);
        return redirect()->back()->with('success', 'Deleted successfully.');
    }

    private function relations(): array
    {
        return [];
    }

    private function relationData(): array
    {
        $relations = [];
        return $relations;
    }
}
