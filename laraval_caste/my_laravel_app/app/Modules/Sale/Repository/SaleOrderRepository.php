<?php

namespace App\Modules\Sale\Repository;

use App\Modules\Sale\Model\SaleOrder;

class SaleOrderRepository implements SaleOrderRepositoryInterface
{
    public function __construct(protected SaleOrder $model) {}

    public function all(array $domain = [], array $with = [])
    {
        $defaultWith = ['order_line_ids', 'customer_id'];
        $eager = array_unique(array_merge($defaultWith, $with));
        $query = $this->model->newQuery()->with($eager);

        // General search across filterable fields (Odoo unified search)
        $search = $domain['search'] ?? $domain['query'] ?? null;
        if (!empty($search)) {$query->where(function($q) use ($search) {
                $q->where('name', 'like', "%{$search}%");
            });
        }

        // Specific field filters (Odoo facet filter chips)
        foreach ($domain as $field => $value) {
            if (in_array($field, ['search', 'query', 'sort_field', 'sort_direction'], true) || $value === null || $value === '') {
                continue;
            }

            if (in_array($field, ['name', 'customer_id', 'order_date', 'state', 'product_id', 'order_id'], true)) {
                if (is_bool($value) || $value === 'true' || $value === 'false') {
                    $boolVal = filter_var($value, FILTER_VALIDATE_BOOLEAN);
                    $query->where($field, $boolVal);
                } else {
                    $query->where($field, 'like', "%{$value}%");
                }
            }
        }

        $sortField = $domain['sort_field'] ?? 'id';
        $sortDirection = $domain['sort_direction'] ?? 'desc';
        if (in_array($sortField, ['id', 'name', 'customer_id', 'order_date', 'state', 'product_id', 'order_id'], true)) {
            $query->orderBy($sortField, strtolower($sortDirection) === 'asc' ? 'asc' : 'desc');
        } else {
            $query->latest();
        }

        return $query->get();
    }

    public function find($id, array $with = [])
    {
        $defaultWith = ['order_line_ids', 'customer_id'];
        $eager = array_unique(array_merge($defaultWith, $with));
        return $this->model->with($eager)->findOrFail($id);
    }

    public function create(array $data)
    {
        $o2mData = [];
        if (isset($data['order_line_ids'])) {
            $o2mData['order_line_ids'] = $data['order_line_ids'];
            unset($data['order_line_ids']);
        }

        $record = $this->model->create($data);

        if (isset($o2mData['order_line_ids']) && is_array($o2mData['order_line_ids'])) {
            foreach ($o2mData['order_line_ids'] as $line) {
                if (is_array($line)) {
                    unset($line['id']);
                    if (!empty(array_filter($line, fn($v) => $v !== null && $v !== '' && $v !== false))) {
                        $record->order_line_ids()->create($line);
                    }
                }
            }
        }

        return $record->load(['order_line_ids', 'customer_id']);
    }

    public function update($id, array $data)
    {
        $record = $this->find($id);
        $o2mData = [];
        if (isset($data['order_line_ids'])) {
            $o2mData['order_line_ids'] = $data['order_line_ids'];
            unset($data['order_line_ids']);
        }

        $record->update($data);

        if (isset($o2mData['order_line_ids']) && is_array($o2mData['order_line_ids'])) {
            $keptIds = [];
            foreach ($o2mData['order_line_ids'] as $line) {
                if (!is_array($line)) continue;
                $lineId = $line['id'] ?? null;
                unset($line['id']);
                if (empty(array_filter($line, fn($v) => $v !== null && $v !== '' && $v !== false))) {
                    continue;
                }
                if ($lineId) {
                    $record->order_line_ids()->where('id', $lineId)->update($line);
                    $keptIds[] = $lineId;
                } else {
                    $created = $record->order_line_ids()->create($line);
                    $keptIds[] = $created->id;
                }
            }
            $record->order_line_ids()->whereNotIn('id', $keptIds)->delete();
        }

        return $record->load(['order_line_ids', 'customer_id']);
    }

    public function delete($id)
    {
        return $this->find($id)->delete();
    }
}
