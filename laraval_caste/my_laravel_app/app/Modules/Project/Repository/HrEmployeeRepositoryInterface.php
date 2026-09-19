<?php

namespace App\Modules\Project\Repository;

interface HrEmployeeRepositoryInterface
{
    public function all(array $filters = [], array $with = []);
    public function find($id, array $with = []);
    public function create(array $data);
    public function update($id, array $data);
    public function delete($id);
}
