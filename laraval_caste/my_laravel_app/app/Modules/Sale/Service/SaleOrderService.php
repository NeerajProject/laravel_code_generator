<?php

namespace App\Modules\Sale\Service;

use App\Modules\Sale\Repository\SaleOrderRepositoryInterface;

class SaleOrderService
{
    public function __construct(protected SaleOrderRepositoryInterface $repository) {}

    public function create(array $data) { return $this->repository->create($data); }
    public function update($id, array $data) { return $this->repository->update($id, $data); }
    public function delete($id) { return $this->repository->delete($id); }
}
