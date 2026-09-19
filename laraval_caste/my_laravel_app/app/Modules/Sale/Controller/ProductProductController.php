<?php

namespace App\Modules\Sale\Controller;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;
use App\Modules\Sale\Model\ProductProduct;
use App\Modules\Sale\Repository\ProductProductRepositoryInterface;
use App\Modules\Sale\Service\ProductProductService;
use App\Modules\Sale\Request\ProductProductRequest;

use App\Http\Controllers\Controller;

class ProductProductController extends Controller
{
    public function __construct(
        protected ProductProductRepositoryInterface $repository,
        protected ProductProductService $service
    ) {}

    public function index(Request $request)
    {
        $query = ProductProduct::query();

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('name', 'like', '%' . $search . '%');
            });
        }

        $records = $query->latest()->paginate(20)->withQueryString();

        return Inertia::render('Sale/ProductProduct/Index', [
            'records' => $records,
            'filters' => $request->only('search'),
        ]);
    }

    public function create()
    {
        return Inertia::render(
            'Sale/ProductProduct/Form',
            [
                'record' => null,
                'relations' => $this->relationData(),
            ]
        );
    }

    public function store(ProductProductRequest $request)
    {
        return DB::transaction(function () use ($request) {
            $data = $request->except(['_token']);
            $record = $this->service->create($data);

            return redirect()->route('product.product.index')->with('success', 'Created successfully.');
        });
    }

    public function show(ProductProduct $record)
    {
        $record->load($this->relations());
        return Inertia::render('Sale/ProductProduct/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
            'readonly' => true,
        ]);
    }

    public function edit(ProductProduct $record)
    {
        $record->load($this->relations());
        return Inertia::render('Sale/ProductProduct/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
        ]);
    }

    public function update(ProductProductRequest $request, ProductProduct $record)
    {
        return DB::transaction(function () use ($request, $record) {
            $data = $request->except(['_token', '_method']);
            $record = $this->service->update($record->id, $data);

            return redirect()->route('product.product.index')->with('success', 'Updated successfully.');
        });
    }

    public function destroy(ProductProduct $record)
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
