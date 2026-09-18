<?php
namespace App\Modules\ResPartner\Controller;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use App\Modules\ResPartner\Repository\ResPartnerRepositoryInterface;
use App\Modules\ResPartner\Service\ResPartnerService;
use App\Modules\ResPartner\Request\ResPartnerRequest;


class ResPartnerController extends Controller
{
    public function __construct(
        protected ResPartnerRepositoryInterface $repository,
        protected ResPartnerService $service
    ) {}

    public function index(Request $request) {
        return Inertia::render('Modules/ResPartner/Index', [
            'records' => $this->repository->all($request->get('filters', [])),
        ]);
    }
    public function create() {
        $lookups = [];
        return Inertia::render('Modules/ResPartner/Form', ['lookups' => $lookups ?? []]);
    }
    public function store(ResPartnerRequest $request) {
        $this->repository->create($request->validated());
        return redirect()->route('res.partner.index');
    }
    public function show($id) {
        return Inertia::render('Modules/ResPartner/Show', ['record' => $this->repository->find($id)]);
    }
    public function edit($id) {
        $lookups = [];
        return Inertia::render('Modules/ResPartner/Form', [
            'record' => $this->repository->find($id),
            'lookups' => $lookups ?? [],
        ]);
    }
    public function update(ResPartnerRequest $request, $id) {$this->repository->update($id,$request->validated());
        return redirect()->route('res.partner.index');
    }
    public function destroy($id) {
        $this->repository->delete($id);
        return redirect()->route('res.partner.index');
    }

}
