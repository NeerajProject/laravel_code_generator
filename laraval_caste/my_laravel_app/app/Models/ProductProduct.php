<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class ProductProduct extends Model
{
    protected $table = 'product_products';

    protected $fillable = [
        'name',
    ];
}
