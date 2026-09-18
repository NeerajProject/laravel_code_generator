<?php

namespace App\Modules\Sale\Repository;

use App\Modules\Sale\Model\SaleOrder;

class SaleOrderRepository implements SaleOrderRepositoryInterface
{
    public function __construct(protected SaleOrder $model) {}

    public function all(array $filters = [], array $with = [])
    {
        $query = $this->model->newQuery()->with($with);
        foreach ($filters as $field => $value) {
            if ($field === 'search' && $value !== null && $value !== '') {
                $query->where(function ($q) use ($value) {
                    $q->where('name', 'like', '%' . $value . '%');
                    $q->orWhere('note', 'like', '%' . $value . '%');
                });
                continue;
            }
            if (in_array($field, ['name', 'customer_id', 'order_date', 'state', 'note'], true) && $value !== null && $value !== '') {
                $query->where($field, $value);
            }
        }
        return $query->latest()->paginate(20)->withQueryString();
    }

    public function find($id, array $with = [])
    {
        return $this->model->with($with)->findOrFail($id);
    }

    public function create(array $data) { return $this->model->create($data); }

    public function update($id, array $data)
    {
        $record = $this->find($id);
        $record->update($data);
        return $record;
    }

    public function delete($id) { return $this->find($id)->delete(); }
}
