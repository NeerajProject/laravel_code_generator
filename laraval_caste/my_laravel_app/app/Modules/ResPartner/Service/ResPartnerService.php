<?php
namespace App\Modules\ResPartner\Service;
use App\Modules\ResPartner\Repository\ResPartnerRepositoryInterface;

class ResPartnerService
{
    public function __construct(protected ResPartnerRepositoryInterface $repository) {}

    public function sale_orderCount($id) {$record = $this->repository->find($id, ['sale_order']);
        return $record->sale_order->count();
    }

}
