<?php

namespace App\Modules\Sale\Request;

use Illuminate\Foundation\Http\FormRequest;

class SaleOrderLineRequest extends FormRequest
{
    public function authorize(): bool { return true; }

    public function rules(): array
    {
        return [
            'order_id' => 'nullable',
            'product_id' => 'nullable',
            'quantity' => 'nullable',
            'unit_price' => 'nullable',
        ];
    }
}
