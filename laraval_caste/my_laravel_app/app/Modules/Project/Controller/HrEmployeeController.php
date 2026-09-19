<?php

namespace App\Modules\Project\Controller;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;
use App\Modules\Project\Model\HrEmployee;
use App\Modules\Project\Repository\HrEmployeeRepositoryInterface;
use App\Modules\Project\Service\HrEmployeeService;
use App\Modules\Project\Request\HrEmployeeRequest;

use App\Http\Controllers\Controller;

class HrEmployeeController extends Controller
{
    public function __construct(
        protected HrEmployeeRepositoryInterface $repository,
        protected HrEmployeeService $service
    ) {}

    public function index(Request $request)
    {
        $query = HrEmployee::query();

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('name', 'like', '%' . $search . '%');
            });
        }

        $records = $query->latest()->paginate(20)->withQueryString();

        return Inertia::render('Project/HrEmployee/Index', [
            'records' => $records,
            'filters' => $request->only('search'),
        ]);
    }

    public function create()
    {
        return Inertia::render(
            'Project/HrEmployee/Form',
            [
                'record' => null,
                'relations' => $this->relationData(),
            ]
        );
    }

    public function store(HrEmployeeRequest $request)
    {
        return DB::transaction(function () use ($request) {
            $data = $request->except(['_token']);
            $record = $this->service->create($data);

            return redirect()->route('hr.employee.index')->with('success', 'Created successfully.');
        });
    }

    public function show(HrEmployee $record)
    {
        $record->load($this->relations());
        return Inertia::render('Project/HrEmployee/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
            'readonly' => true,
        ]);
    }

    public function edit(HrEmployee $record)
    {
        $record->load($this->relations());
        return Inertia::render('Project/HrEmployee/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
        ]);
    }

    public function update(HrEmployeeRequest $request, HrEmployee $record)
    {
        return DB::transaction(function () use ($request, $record) {
            $data = $request->except(['_token', '_method']);
            $record = $this->service->update($record->id, $data);

            return redirect()->route('hr.employee.index')->with('success', 'Updated successfully.');
        });
    }

    public function destroy(HrEmployee $record)
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
