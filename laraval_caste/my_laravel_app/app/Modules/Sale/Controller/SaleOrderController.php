<?php

namespace App\Modules\Sale\Controller;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use App\Modules\Sale\Repository\SaleOrderRepositoryInterface;
use App\Modules\Sale\Service\SaleOrderService;
use App\Modules\Sale\Request\SaleOrderRequest;

class SaleOrderController extends Controller
{
    public function __construct(
        protected SaleOrderRepositoryInterface $repository,
        protected SaleOrderService $service
    ) {}

    public function index(Request $request)
    {
        $filters = $request->get('filters', []);
        if ($request->has('search') && !isset($filters['search'])) {
            $filters['search'] = $request->get('search');
        }

        return Inertia::render('Modules/Sale/SaleOrder/Index', [
            'records' => $this->repository->all($filters),
            'filters' => $filters,
        ]);
    }

    public function create()
    {
        return Inertia::render('Modules/Sale/SaleOrder/Form', [
            'record' => null,
            'lookups' => [],
        ]);
    }

    public function store(SaleOrderRequest $request)
    {
        $this->repository->create($request->validated());
        return redirect()->route('sale.order.index');
    }

    public function show($id)
    {
        return Inertia::render('Modules/Sale/SaleOrder/Show', [
            'record' => $this->repository->find($id),
        ]);
    }

    public function edit($id)
    {
        return Inertia::render('Modules/Sale/SaleOrder/Form', [
            'record' => $this->repository->find($id),
            'lookups' => [],
        ]);
    }

    public function update(SaleOrderRequest $request, $id)
    {
        $this->repository->update($id, $request->validated());
        return redirect()->route('sale.order.index');
    }

    public function destroy($id)
    {
        $this->repository->delete($id);
        return redirect()->route('sale.order.index');
    }
}
