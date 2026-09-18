<?php

namespace App\Modules\Project\Model;

use Illuminate\Database\Eloquent\Model;

class ProjectProject extends Model
{
    protected $table = 'project_projects';

    protected $fillable = [
        'name',
        'code',
        'description',
        'is_active'
    ];
    protected $casts = [
        'is_active' => 'boolean',
    ];

    protected $appends = [
        
    ];

    public function task_ids()
    {
        return $this->hasMany(\App\Modules\Project\Model\ProjectTask::class, 'project_project_id');
    }
}
