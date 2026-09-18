<?php

namespace App\Modules\Sale\Request;

use Illuminate\Foundation\Http\FormRequest;

class SaleOrderRequest extends FormRequest
{
    public function authorize(): bool { return true; }

    public function rules(): array
    {
        return [
            'name' => 'required',
            'customer_id' => 'nullable',
            'order_date' => 'nullable',
            'state' => 'nullable',
            'note' => 'nullable',
        ];
    }
}
