<?php

namespace App\Modules\Project\Service;

use App\Modules\Project\Repository\ProjectProjectRepositoryInterface;

class ProjectProjectService
{
    public function __construct(protected ProjectProjectRepositoryInterface $repository) {}

    public function create(array $data) { return $this->repository->create($data); }
    public function update($id, array $data) { return $this->repository->update($id, $data); }
    public function delete($id) { return $this->repository->delete($id); }
}
