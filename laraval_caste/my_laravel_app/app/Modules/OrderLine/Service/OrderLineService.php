<?php
namespace App\Modules\OrderLine\Service;
use App\Modules\OrderLine\Repository\OrderLineRepositoryInterface;

class OrderLineService
{
    public function __construct(protected OrderLineRepositoryInterface $repository) {}

}
