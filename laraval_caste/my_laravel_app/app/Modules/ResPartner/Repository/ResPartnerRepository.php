<?php
namespace App\Modules\ResPartner\Repository;
use App\Modules\ResPartner\Model\ResPartner;

class ResPartnerRepository implements ResPartnerRepositoryInterface
{
    public function __construct(protected ResPartner $model) {}

    /** Filterable fields for domain-style search: ['name', 'email', 'phone'] */
    public function all(array $domain = [], array$with = []) {
        $query = $this->model->newQuery()->with($with);
        foreach ($domain as $field => $value) {
            if (in_array($field, ['name', 'email', 'phone'], true) && $value !== null && $value !== '') {
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
