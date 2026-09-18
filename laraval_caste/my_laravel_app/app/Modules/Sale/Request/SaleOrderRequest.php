<?php

namespace App\Modules\Sale\Request;

use Illuminate\Foundation\Http\FormRequest;

class SaleOrderRequest extends FormRequest
{
    public function authorize(): bool { return true; }

    public function rules(): array
    {
        return [
            'name' => 'required|string|max:255',
            'customer_id' => 'nullable|string|max:255',
            'order_date' => 'nullable|string|max:255',
            'state' => 'nullable|string|max:255',
            'note' => 'nullable|string',
            'order_line_ids' => 'nullable|array',
            'order_line_ids.*.name' => 'nullable|string|max:255',
            'order_line_ids.*.quantity' => 'nullable|numeric',
            'order_line_ids.*.price_unit' => 'nullable|numeric',
            'order_line_ids.*.subtotal' => 'nullable|numeric',
        ];
    }
}
