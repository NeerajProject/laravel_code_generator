<?php

namespace App\Modules\Sale\Model;

use Illuminate\Database\Eloquent\Model;

class SaleOrderLine extends Model
{
    protected $table = 'sale_order_lines';

    protected $fillable = [
        'sale_order_id',
        'name',
        'description',
        'is_done',
    ];

    protected $casts = [
        'is_done' => 'boolean',
    ];

    public function project()
    {
        return $this->belongsTo(SaleOrder::class, 'sale_order_id');
    }
}
