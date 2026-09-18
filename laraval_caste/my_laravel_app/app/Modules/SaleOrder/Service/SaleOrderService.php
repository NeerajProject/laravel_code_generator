<?php
namespace App\Modules\SaleOrder\Service;
use App\Modules\SaleOrder\Repository\SaleOrderRepositoryInterface;

class SaleOrderService
{
    public function __construct(protected SaleOrderRepositoryInterface $repository) {}

    public function submit($id) {$record = $this->repository->find($id);
        // TODO: implement submit logic
        return $record;
    }

    public function invoiceCount($id) {$record = $this->repository->find($id, ['invoice']);
        return $record->invoice->count();
    }

    public function deliveryCount($id) {$record = $this->repository->find($id, ['delivery']);
        return $record->delivery->count();
    }

}
