<?php

namespace App\Modules\Sale\Controller;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;
use App\Modules\Sale\Model\ResPartner;
use App\Modules\Sale\Repository\ResPartnerRepositoryInterface;
use App\Modules\Sale\Service\ResPartnerService;
use App\Modules\Sale\Request\ResPartnerRequest;

use App\Http\Controllers\Controller;

class ResPartnerController extends Controller
{
    public function __construct(
        protected ResPartnerRepositoryInterface $repository,
        protected ResPartnerService $service
    ) {}

    public function index(Request $request)
    {
        $query = ResPartner::query();

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('name', 'like', '%' . $search . '%');
            });
        }

        $records = $query->latest()->paginate(20)->withQueryString();

        return Inertia::render('Sale/ResPartner/Index', ['records' => $records]);
    }

    public function create()
    {
        return Inertia::render(
            'Sale/ResPartner/Form',
            [
                'record' => null,
                'relations' => $this->relationData(),
            ]
        );
    }

    public function store(ResPartnerRequest $request)
    {
        return DB::transaction(function () use ($request) {
            $data = $request->except(['_token']);
            $record = $this->service->create($data);


        });
    }

    public function show(ResPartner $record)
    {
        $record->load($this->relations());
        return Inertia::render('Sale/ResPartner/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
            'readonly' => true,
        ]);
    }

    public function edit(ResPartner $record)
    {
        $record->load($this->relations());
        return Inertia::render('Sale/ResPartner/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
        ]);
    }

    public function update(ResPartnerRequest $request, ResPartner $record)
    {
        return DB::transaction(function () use ($request, $record) {
            $data = $request->except(['_token', '_method']);
            $record = $this->service->update($record->id, $data);

            return redirect()->route('res.partner.index')->with('success', 'Updated successfully.');
        });
    }

    public function destroy(ResPartner $record)
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
