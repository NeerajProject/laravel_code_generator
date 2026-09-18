<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class ResPartner extends Model
{
    protected $table = 'res_partners';

    protected $fillable = [
        'name',
    ];
}
