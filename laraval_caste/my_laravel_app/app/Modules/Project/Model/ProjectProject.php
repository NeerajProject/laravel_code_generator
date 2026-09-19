<?php

namespace App\Modules\Project\Model;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

use App\Modules\Project\Model\ResUsers;
use App\Modules\Project\Model\ProjectTask;

class ProjectProject extends Model
{
    protected $table = 'project_projects';

    protected $fillable = [
        'name',
        'manager_id',
        'start_date',
        'end_date',
        'state',
        'description',
    ];

    protected $casts = [
        'start_date' => 'date',
        'end_date' => 'date',
    ];

    public function manager(): BelongsTo
    {
        return $this->belongsTo(ResUsers::class, 'manager_id');
    }

    public function task_ids(): HasMany
    {
        return $this->hasMany(ProjectTask::class, 'project_id');
    }
}
