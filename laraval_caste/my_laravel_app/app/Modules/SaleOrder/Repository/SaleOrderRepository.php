<?php
namespace App\Modules\SaleOrder\Repository;
use App\Modules\SaleOrder\Model\SaleOrder;

class SaleOrderRepository implements SaleOrderRepositoryInterface
{
    public function __construct(protected SaleOrder $model) {}

    /** Filterable fields for domain-style search: ['name', 'customer_id'] */
    public function all(array $domain = [], array$with = []) {
        $query = $this->model->newQuery()->with($with);
        foreach ($domain as $field => $value) {
            if (in_array($field, ['name', 'customer_id'], true) && $value !== null && $value !== '') {
                $query->where($field, $value);
            }
        }
        return $query->latest()->get();
    }
    public function find($id, array $with = []) { return $this->model->with($with)->findOrFail($id); }
    public function create(array $data) { return $this->model->create($data); }
    public function update($id, array $data) {$record = $this->find($id);
        $record->update($data);
        return $record;
    }
    public function delete($id) { return $this->find($id)->delete(); }
}
