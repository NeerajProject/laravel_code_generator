<?php

namespace App\Modules\Project\Model;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;


class ResUsers extends Model
{
    protected $table = 'res_users';

    protected $fillable = [
        'name',
    ];
}
