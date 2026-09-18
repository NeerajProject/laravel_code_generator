<?php
namespace App\Modules\ResPartner\Request;
use Illuminate\Foundation\Http\FormRequest;

class ResPartnerRequest extends FormRequest
{
    public function authorize(): bool { return true; }
    public function rules(): array {
        return [
            'name' => 'required',
            'email' => 'nullable',
            'phone' => 'nullable',
            'address' => 'nullable',
            'is_active' => 'nullable',
        ];
    }
}
