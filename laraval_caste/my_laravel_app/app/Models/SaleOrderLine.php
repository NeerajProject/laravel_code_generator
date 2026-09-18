<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class SaleOrderLine extends Model
{
    protected $table = 'sale_order_lines';

    protected $fillable = [
        'order_id',
        'product_id',
        'quantity',
        'unit_price',
        'subtotal',
    ];
        'quantity' => 'float',
        'unit_price' => 'float',
        'subtotal' => 'float',

    public function order(): BelongsTo
    {
        return $this->belongsTo(SaleOrder::class, 'order_id');
    }

    public function product(): BelongsTo
    {
        return $this->belongsTo(ProductProduct::class, 'product_id');
    }
}
