<?php
namespace App\Modules\OrderLine\Model;
use Illuminate\Database\Eloquent\Model;

class OrderLine extends Model
{
    protected $table = 'order_lines';
    protected $fillable = [
        'order_id',
        'product_name',
        'quantity',
        'price_unit',
        'subtotal'
    ];
    protected $casts = [
        'quantity' => 'float',
        'price_unit' => 'float',
        'subtotal' => 'float',
    ];

    protected $appends = [
        
    ];

    public function order_id()
    {
        return $this->belongsTo(\App\Modules\SaleOrder\Model\SaleOrder::class, 'order_id');
    }

}
