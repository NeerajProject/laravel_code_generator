<?php

namespace App\Modules\Project\Model;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

use App\Modules\Project\Model\ProjectProject;
use App\Modules\Project\Model\ResUsers;
use App\Modules\Project\Model\ProjectTimesheet;

class ProjectTask extends Model
{
    protected $table = 'project_tasks';

    protected $fillable = [
        'name',
        'project_id',
        'assignee_id',
        'deadline',
        'state',
        'description',
        'total_hours',
    ];

    protected $casts = [
        'deadline' => 'date',
        'total_hours' => 'float',
    ];

    public function project(): BelongsTo
    {
        return $this->belongsTo(ProjectProject::class, 'project_id');
    }

    public function assignee(): BelongsTo
    {
        return $this->belongsTo(ResUsers::class, 'assignee_id');
    }

    public function timesheet_ids(): HasMany
    {
        return $this->hasMany(ProjectTimesheet::class, 'task_id');
    }
}
