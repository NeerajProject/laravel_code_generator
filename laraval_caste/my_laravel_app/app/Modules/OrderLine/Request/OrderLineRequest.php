<?php
namespace App\Modules\OrderLine\Request;
use Illuminate\Foundation\Http\FormRequest;

class OrderLineRequest extends FormRequest
{
    public function authorize(): bool { return true; }
    public function rules(): array {
        return [
            'order_id' => 'nullable',
            'product_name' => 'required',
            'quantity' => 'nullable',
            'price_unit' => 'nullable',
            'subtotal' => 'nullable',
        ];
    }
}
