<?php

namespace App\Modules\Sale\Model;

use Illuminate\Database\Eloquent\Model;

class SaleOrder extends Model
{
    protected $table = 'sale_orders';

    protected $fillable = [
        'name',
        'customer_id',
        'order_date',
        'state',
        'amount_total',
        'note'
    ];
    protected $casts = [
        'order_date' => 'date',
        'amount_total' => 'float',
    ];

    protected $appends = [
        'amount_total'
    ];

    public function customer_id()
    {
        return $this->belongsTo(\App\Modules\Sale\Model\ResPartner::class, 'customer_id');
    }

    public function order_line_ids()
    {
        return $this->hasMany(\App\Modules\Sale\Model\SaleOrderLine::class, 'sale_order_id');
    }

    public function getAmountTotalAttribute()
    {
        return $this->order_line_ids->sum('subtotal');
    }

    public function getComputeSubtotalAttribute()
    {
        return 0;
    }
}
