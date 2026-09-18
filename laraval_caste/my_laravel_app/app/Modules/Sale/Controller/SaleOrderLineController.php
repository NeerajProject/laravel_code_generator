<?php

namespace App\Modules\Sale\Controller;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;
use App\Modules\Sale\Model\SaleOrderLine;
use App\Modules\Sale\Repository\SaleOrderLineRepositoryInterface;
use App\Modules\Sale\Service\SaleOrderLineService;
use App\Modules\Sale\Request\SaleOrderLineRequest;
use App\Modules\Sale\Model\SaleOrder;
use App\Modules\Sale\Model\ProductProduct;

use App\Http\Controllers\Controller;

class SaleOrderLineController extends Controller
{
    public function __construct(
        protected SaleOrderLineRepositoryInterface $repository,
        protected SaleOrderLineService $service
    ) {}

    public function index(Request $request)
    {
        $query = SaleOrderLine::query();
        $query->with(['order', 'product']);

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->whereKey(0);
            });
        }

        $records = $query->latest()->paginate(20)->withQueryString();

        return Inertia::render('Sale/SaleOrderLine/Index', ['records' => $records]);
    }

    public function create()
    {
        return Inertia::render(
            'Sale/SaleOrderLine/Form',
            [
                'record' => null,
                'relations' => $this->relationData(),
            ]
        );
    }

    public function store(SaleOrderLineRequest $request)
    {
        return DB::transaction(function () use ($request) {
            $data = $request->except(['_token']);
            unset($data['subtotal']);
            $record = $this->service->create($data);

            return redirect()->route('sale.order.line.index')->with('success', 'Created successfully.');
        });
    }

    public function show(SaleOrderLine $record)
    {
        $record->load($this->relations());
        return Inertia::render('Sale/SaleOrderLine/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
            'readonly' => true,
        ]);
    }

    public function edit(SaleOrderLine $record)
    {
        $record->load($this->relations());
        return Inertia::render('Sale/SaleOrderLine/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
        ]);
    }

    public function update(SaleOrderLineRequest $request, SaleOrderLine $record)
    {
        return DB::transaction(function () use ($request, $record) {
            $data = $request->except(['_token', '_method']);
            unset($data['subtotal']);
            $record = $this->service->update($record->id, $data);

            return redirect()->route('sale.order.line.index')->with('success', 'Updated successfully.');
        });
    }

    public function destroy(SaleOrderLine $record)
    {
        $this->service->delete($record->id);
        return redirect()->back()->with('success', 'Deleted successfully.');
    }

    private function relations(): array
    {
        return ["order", "product"];
    }

    private function relationData(): array
    {
        $relations = [];
        $relations['order_id'] = SaleOrder::orderBy('name')->get(['id', 'name']);
        $relations['product_id'] = ProductProduct::orderBy('name')->get(['id', 'name']);
        return $relations;
    }
}
