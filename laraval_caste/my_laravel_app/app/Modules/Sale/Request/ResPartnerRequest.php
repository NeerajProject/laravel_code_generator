<?php

namespace App\Modules\Sale\Request;

use Illuminate\Foundation\Http\FormRequest;

class ResPartnerRequest extends FormRequest
{
    public function authorize(): bool { return true; }

    public function rules(): array
    {
        return [
            'name' => 'nullable',
        ];
    }
}
