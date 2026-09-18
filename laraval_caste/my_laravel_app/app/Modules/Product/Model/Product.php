<?php

namespace App\Modules\Product\Model;

use Illuminate\Database\Eloquent\Model;

class ProductProduct extends Model
{
    protected $table = 'product_products';

    protected $fillable = [
        'name',
        'code',
        'list_price',
        'standard_price',
        'description',
        'is_active'
    ];
    protected $casts = [
        'list_price' => 'float',
        'standard_price' => 'float',
        'is_active' => 'boolean',
    ];

    protected $appends = [
        
    ];
}
