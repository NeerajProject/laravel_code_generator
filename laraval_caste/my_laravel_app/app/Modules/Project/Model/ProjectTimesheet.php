<?php

namespace App\Modules\Project\Model;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

use App\Modules\Project\Model\ProjectTask;
use App\Modules\Project\Model\HrEmployee;

class ProjectTimesheet extends Model
{
    protected $table = 'project_timesheets';

    protected $fillable = [
        'date',
        'task_id',
        'employee_id',
        'description',
        'hours',
    ];

    protected $casts = [
        'date' => 'date',
        'hours' => 'float',
    ];

    public function task(): BelongsTo
    {
        return $this->belongsTo(ProjectTask::class, 'task_id');
    }

    public function employee(): BelongsTo
    {
        return $this->belongsTo(HrEmployee::class, 'employee_id');
    }
}
