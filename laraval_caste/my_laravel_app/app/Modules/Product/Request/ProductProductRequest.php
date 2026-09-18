<?php

namespace App\Modules\Product\Request;

use Illuminate\Foundation\Http\FormRequest;

class ProductProductRequest extends FormRequest
{
    public function authorize(): bool { return true; }

    public function rules(): array {
        return [
            'name' => 'required',
            'code' => 'nullable',
            'list_price' => 'nullable',
            'standard_price' => 'nullable',
            'description' => 'nullable',
            'is_active' => 'nullable',
        ];
    }
}
