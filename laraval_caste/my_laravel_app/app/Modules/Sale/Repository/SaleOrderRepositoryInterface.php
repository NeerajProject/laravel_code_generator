<?php

namespace App\Modules\Sale\Repository;

interface SaleOrderRepositoryInterface
{
    public function all(array $filters = [], array $with = []);
    public function find($id, array $with = []);
    public function create(array $data);
    public function update($id, array $data);
    public function delete($id);
}
