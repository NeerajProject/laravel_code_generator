<?php

namespace App\Modules\Project\Repository;

use App\Modules\Project\Model\ProjectProject;

class ProjectProjectRepository implements ProjectProjectRepositoryInterface
{
    public function __construct(protected ProjectProject $model) {}

    public function all(array $domain = [], array $with = [])
    {
        $defaultWith = ['task_ids'];
        $eager = array_unique(array_merge($defaultWith, $with));
        $query = $this->model->newQuery()->with($eager);

        // General search across filterable fields (Odoo unified search)
        $search = $domain['search'] ?? $domain['query'] ?? null;
        if (!empty($search)) {$query->where(function($q) use ($search) {
                $q->where('name', 'like', "%{$search}%");
                $q->orWhere('code', 'like', "%{$search}%");
            });
        }

        // Specific field filters (Odoo facet filter chips)
        foreach ($domain as $field => $value) {
            if (in_array($field, ['search', 'query', 'sort_field', 'sort_direction'], true) || $value === null || $value === '') {
                continue;
            }

            if (in_array($field, ['name', 'code', 'name', 'code', 'project_id'], true)) {
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
        if (in_array($sortField, ['id', 'name', 'code', 'name', 'code', 'project_id'], true)) {
            $query->orderBy($sortField, strtolower($sortDirection) === 'asc' ? 'asc' : 'desc');
        } else {
            $query->latest();
        }

        return $query->get();
    }

    public function find($id, array $with = [])
    {
        $defaultWith = ['task_ids'];
        $eager = array_unique(array_merge($defaultWith, $with));
        return $this->model->with($eager)->findOrFail($id);
    }

    public function create(array $data)
    {
        $o2mData = [];
        if (isset($data['task_ids'])) {
            $o2mData['task_ids'] = $data['task_ids'];
            unset($data['task_ids']);
        }

        $record = $this->model->create($data);

        if (isset($o2mData['task_ids']) && is_array($o2mData['task_ids'])) {
            foreach ($o2mData['task_ids'] as $line) {
                if (is_array($line)) {
                    unset($line['id']);
                    if (!empty(array_filter($line, fn($v) => $v !== null && $v !== '' && $v !== false))) {
                        $record->task_ids()->create($line);
                    }
                }
            }
        }

        return $record->load(['task_ids']);
    }

    public function update($id, array $data)
    {
        $record = $this->find($id);
        $o2mData = [];
        if (isset($data['task_ids'])) {
            $o2mData['task_ids'] = $data['task_ids'];
            unset($data['task_ids']);
        }

        $record->update($data);

        if (isset($o2mData['task_ids']) && is_array($o2mData['task_ids'])) {
            $keptIds = [];
            foreach ($o2mData['task_ids'] as $line) {
                if (!is_array($line)) continue;
                $lineId = $line['id'] ?? null;
                unset($line['id']);
                if (empty(array_filter($line, fn($v) => $v !== null && $v !== '' && $v !== false))) {
                    continue;
                }
                if ($lineId) {
                    $record->task_ids()->where('id', $lineId)->update($line);
                    $keptIds[] = $lineId;
                } else {
                    $created = $record->task_ids()->create($line);
                    $keptIds[] = $created->id;
                }
            }
            $record->task_ids()->whereNotIn('id', $keptIds)->delete();
        }

        return $record->load(['task_ids']);
    }

    public function delete($id)
    {
        return $this->find($id)->delete();
    }
}
