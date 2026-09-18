<?php

namespace App\Modules\Product\Service;

use App\Modules\Product\Repository\ProductProductRepositoryInterface;

class ProductProductService
{
    public function __construct(protected ProductProductRepositoryInterface $repository) {}

}
