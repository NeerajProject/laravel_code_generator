<?php

namespace App\Modules\Project\Service;

use App\Modules\Project\Repository\ProjectProjectRepositoryInterface;

class ProjectProjectService
{
    public function __construct(protected ProjectProjectRepositoryInterface $repository) {}

}
