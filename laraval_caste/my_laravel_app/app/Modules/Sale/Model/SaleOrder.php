<?php

namespace App\Modules\Sale\Model;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

use App\Modules\Sale\Model\ResPartner;
use App\Modules\Sale\Model\SaleOrderLine;

class SaleOrder extends Model
{
    protected $table = 'sale_orders';

    protected $fillable = [
        'name',
        'customer_id',
        'order_date',
        'state',
        'amount_total',
        'note',
    ];

    protected $casts = [
        'order_date' => 'date',
        'amount_total' => 'float',
    ];

    public function customer(): BelongsTo
    {
        return $this->belongsTo(ResPartner::class, 'customer_id');
    }

    public function order_line_ids(): HasMany
    {
        return $this->hasMany(SaleOrderLine::class, 'order_id');
    }
}
