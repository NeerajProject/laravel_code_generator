<?php

namespace App\Modules\Sale\Service;

use App\Modules\Sale\Repository\SaleOrderRepositoryInterface;

class SaleOrderService
{
    public function __construct(protected SaleOrderRepositoryInterface $repository) {}

}
