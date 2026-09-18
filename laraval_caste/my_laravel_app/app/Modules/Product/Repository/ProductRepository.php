<?php

namespace App\Modules\Product\Repository;

use App\Modules\Product\Model\ProductProduct;

class ProductProductRepository implements ProductProductRepositoryInterface
{
    public function __construct(protected ProductProduct $model) {}

    public function all(array $domain = [], array $with = []) {$query = $this->model->newQuery()->with($with);
        foreach ($domain as $field =>$value) {
            if (in_array($field, ['name', 'code'], true) &&$value !== null && $value !== '') {$query->where($field,$value);
            }
        }
        return $query->latest()->get();
    }

    public function find($id, array$with = []) {
        return $this->model->with($with)->findOrFail($id);
    }

    public function create(array $data) {
        return $this->model->create($data);
    }

    public function update($id, array $data) {$record = $this->find($id);
        $record->update($data);
        return $record;
    }

    public function delete($id) {
        return $this->find($id)->delete();
    }
}
