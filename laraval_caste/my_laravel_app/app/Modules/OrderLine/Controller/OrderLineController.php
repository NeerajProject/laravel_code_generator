<?php
namespace App\Modules\OrderLine\Controller;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use App\Modules\OrderLine\Repository\OrderLineRepositoryInterface;
use App\Modules\OrderLine\Service\OrderLineService;
use App\Modules\OrderLine\Request\OrderLineRequest;

class OrderLineController extends Controller
{
    public function __construct(
        protected OrderLineRepositoryInterface $repository,
        protected OrderLineService $service
    ) {}

    public function index(Request $request) {
        return Inertia::render('Modules/OrderLine/Index', [
            'records' => $this->repository->all($request->get('filters', [])),
        ]);
    }
    public function create() { return Inertia::render('Modules/OrderLine/Form'); }
    public function store(OrderLineRequest $request) {
        $this->repository->create($request->validated());
        return redirect()->route('order.line.index');
    }
    public function show($id) {
        return Inertia::render('Modules/OrderLine/Show', ['record' => $this->repository->find($id)]);
    }
    public function edit($id) {
        return Inertia::render('Modules/OrderLine/Form', ['record' => $this->repository->find($id)]);
    }
    public function update(OrderLineRequest $request, $id) {$this->repository->update($id,$request->validated());
        return redirect()->route('order.line.index');
    }
    public function destroy($id) {
        $this->repository->delete($id);
        return redirect()->route('order.line.index');
    }

}
