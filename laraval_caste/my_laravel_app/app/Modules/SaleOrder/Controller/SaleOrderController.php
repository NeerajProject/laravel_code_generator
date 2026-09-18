<?php
namespace App\Modules\SaleOrder\Controller;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use App\Modules\SaleOrder\Repository\SaleOrderRepositoryInterface;
use App\Modules\SaleOrder\Service\SaleOrderService;
use App\Modules\SaleOrder\Request\SaleOrderRequest;

class SaleOrderController extends Controller
{
    public function __construct(
        protected SaleOrderRepositoryInterface $repository,
        protected SaleOrderService $service
    ) {}

    public function index(Request $request) {
        return Inertia::render('Modules/SaleOrder/Index', [
            'records' => $this->repository->all($request->get('filters', [])),
        ]);
    }
    public function create() { return Inertia::render('Modules/SaleOrder/Form'); }
    public function store(SaleOrderRequest $request) {
        $this->repository->create($request->validated());
        return redirect()->route('sale.order.index');
    }
    public function show($id) {
        return Inertia::render('Modules/SaleOrder/Show', ['record' => $this->repository->find($id)]);
    }
    public function edit($id) {
        return Inertia::render('Modules/SaleOrder/Form', ['record' => $this->repository->find($id)]);
    }
    public function update(SaleOrderRequest $request, $id) {$this->repository->update($id,$request->validated());
        return redirect()->route('sale.order.index');
    }
    public function destroy($id) {
        $this->repository->delete($id);
        return redirect()->route('sale.order.index');
    }

    public function submit($id) {
        $this->service->submit($id);
        return redirect()->route('sale.order.show', $id);
    }

}
