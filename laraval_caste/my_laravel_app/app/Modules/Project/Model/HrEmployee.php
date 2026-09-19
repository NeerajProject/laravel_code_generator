<?php

namespace App\Modules\Project\Model;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;


class HrEmployee extends Model
{
    protected $table = 'hr_employees';

    protected $fillable = [
        'name',
    ];
}
