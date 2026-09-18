<?php

namespace App\Modules\Product\Repository;

interface ProductProductRepositoryInterface
{
    public function all(array $domain = [], array$with = []);
    public function find($id, array$with = []);
    public function create(array $data);
    public function update($id, array$data);
    public function delete($id);
}
