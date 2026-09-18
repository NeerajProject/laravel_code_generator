<?php
namespace App\Modules\ResPartner\Repository;

interface ResPartnerRepositoryInterface
{
    public function all(array $domain = [], array$with = []);
    public function find($id, array$with = []);
    public function create(array $data);
    public function update($id, array$data);
    public function delete($id);
}
