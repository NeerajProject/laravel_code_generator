<?php

namespace App\Modules\Project\Model;

use Illuminate\Database\Eloquent\Model;

class ProjectTask extends Model
{
    protected $table = 'project_tasks';

    protected $fillable = [
        'project_project_id',
        'name',
        'description',
        'is_done',
    ];

    protected $casts = [
        'is_done' => 'boolean',
    ];

    public function project()
    {
        return $this->belongsTo(ProjectProject::class, 'project_project_id');
    }
}
