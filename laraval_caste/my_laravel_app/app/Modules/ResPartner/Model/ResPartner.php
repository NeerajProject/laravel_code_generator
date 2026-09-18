<?php
namespace App\Modules\ResPartner\Model;
use Illuminate\Database\Eloquent\Model;

class ResPartner extends Model
{
    protected $table = 'res_partners';
    protected $fillable = [
        'name',
        'email',
        'phone',
        'address',
        'is_active'
    ];
    protected $casts = [
        'is_active' => 'boolean',
    ];

    protected $appends = [
        
    ];

}
