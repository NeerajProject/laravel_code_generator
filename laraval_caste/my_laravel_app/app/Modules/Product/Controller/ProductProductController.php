<?php

namespace App\Modules\Product\Controller;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use App\Modules\Product\Repository\ProductProductRepositoryInterface;
use App\Modules\Product\Service\ProductProductService;
use App\Modules\Product\Request\ProductProductRequest;

class ProductProductController extends Controller
{
    public function __construct(
        protected ProductProductRepositoryInterface $repository,
        protected ProductProductService $service
    ) {}

    public function index(Request $request) {
        return Inertia::render('Modules/Product/ProductProduct/Index', [
            'records' => $this->repository->all($request->get('filters', [])),
        ]);
    }

    public function create() {
        return Inertia::render('Modules/Product/ProductProduct/Form');
    }

    public function store(ProductProductRequest $request) {
        $this->repository->create($request->validated());
        return redirect()->route('product.product.index');
    }

    public function show($id) {
        return Inertia::render('Modules/Product/ProductProduct/Show', [
            'record' => $this->repository->find($id)
        ]);
    }

    public function edit($id) {
        return Inertia::render('Modules/Product/ProductProduct/Form', [
            'record' => $this->repository->find($id)
        ]);
    }

    public function update(ProductProductRequest $request, $id) {$this->repository->update($id,$request->validated());
        return redirect()->route('product.product.index');
    }

    public function destroy($id) {
        $this->repository->delete($id);
        return redirect()->route('product.product.index');
    }
}
