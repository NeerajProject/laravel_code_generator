<?php
namespace App\Modules\SaleOrder\Model;
use Illuminate\Database\Eloquent\Model;

class SaleOrder extends Model
{
    protected $table = 'sale_orders';
    protected $fillable = [
        'name',
        'customer_id',
        'amount_total'
    ];
    protected $casts = [
        'amount_total' => 'float',
    ];

    protected $appends = [
        'amount_total'
    ];

    public function customer_id()
    {
        return $this->belongsTo(\App\Modules\ResPartner\Model\ResPartner::class, 'customer_id');
    }

    public function order_line()
    {
        return $this->hasMany(\App\Modules\OrderLine\Model\OrderLine::class, 'sale_order_id');
    }

    public function getAmountTotalAttribute()
    {
        return $this->order_line->sum('subtotal');
    }

}
