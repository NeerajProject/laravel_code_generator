<?php

namespace App\Modules\Sale\Controller;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;
use App\Modules\Sale\Model\SaleOrder;
use App\Modules\Sale\Repository\SaleOrderRepositoryInterface;
use App\Modules\Sale\Service\SaleOrderService;
use App\Modules\Sale\Request\SaleOrderRequest;
use App\Modules\Sale\Model\ResPartner;
use App\Modules\Sale\Model\ProductProduct;

use App\Http\Controllers\Controller;

class SaleOrderController extends Controller
{
    public function __construct(
        protected SaleOrderRepositoryInterface $repository,
        protected SaleOrderService $service
    ) {}

    public function index(Request $request)
    {
        $query = SaleOrder::query();
        $query->with(['customer', 'order_line_ids']);

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('name', 'like', '%' . $search . '%');
                $q->orWhere('note', 'like', '%' . $search . '%');
            });
        }

        $records = $query->latest()->paginate(20)->withQueryString();

        return Inertia::render('Sale/SaleOrder/Index', [
            'records' => $records,
            'filters' => $request->only('search'),
        ]);
    }

    public function create()
    {
        return Inertia::render(
            'Sale/SaleOrder/Form',
            [
                'record' => null,
                'relations' => $this->relationData(),
            ]
        );
    }

    public function store(SaleOrderRequest $request)
    {
        return DB::transaction(function () use ($request) {
            $data = $request->except(['_token']);
            unset($data['amount_total']);
            unset($data['order_line_ids']);
            $record = $this->service->create($data);

            foreach ($request->input('order_line_ids', []) as $lineData) {
                $lineData['order_id'] = $record->id;
                $lineData['subtotal'] = ($lineData['quantity'] ?? 0) * ($lineData['unit_price'] ?? 0);
                SaleOrderLine::create($lineData);
            }

            $record->update([
                'amount_total' => $record->order_line_ids()->sum('subtotal'),
            ]);

            return redirect()->route('sale.order.index')->with('success', 'Created successfully.');
        });
    }

    public function show(SaleOrder $record)
    {
        $record->load($this->relations());
        return Inertia::render('Sale/SaleOrder/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
            'readonly' => true,
        ]);
    }

    public function edit(SaleOrder $record)
    {
        $record->load($this->relations());
        return Inertia::render('Sale/SaleOrder/Form', [
            'record' => $record,
            'relations' => $this->relationData(),
        ]);
    }

    public function update(SaleOrderRequest $request, SaleOrder $record)
    {
        return DB::transaction(function () use ($request, $record) {
            $data = $request->except(['_token', '_method']);
            unset($data['amount_total']);
            unset($data['order_line_ids']);
            $record = $this->service->update($record->id, $data);
            $record->order_line_ids()->delete();

            foreach ($request->input('order_line_ids', []) as $lineData) {
                $lineData['order_id'] = $record->id;
                $lineData['subtotal'] = ($lineData['quantity'] ?? 0) * ($lineData['unit_price'] ?? 0);
                SaleOrderLine::create($lineData);
            }

            $record->update([
                'amount_total' => $record->order_line_ids()->sum('subtotal'),
            ]);

            return redirect()->route('sale.order.index')->with('success', 'Updated successfully.');
        });
    }

    public function destroy(SaleOrder $record)
    {
        $this->service->delete($record->id);
        return redirect()->back()->with('success', 'Deleted successfully.');
    }

    private function relations(): array
    {
        return ["customer", "order_line_ids"];
    }

    private function relationData(): array
    {
        $relations = [];
        $relations['customer_id'] = ResPartner::orderBy('name')->get(['id', 'name']);
        $relations['product_id'] = ProductProduct::orderBy('name')->get(['id', 'name']);
        return $relations;
    }
}
