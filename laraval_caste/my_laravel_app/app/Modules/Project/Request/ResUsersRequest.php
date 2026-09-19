<?php

namespace App\Modules\Project\Request;

use Illuminate\Foundation\Http\FormRequest;

class ResUsersRequest extends FormRequest
{
    public function authorize(): bool { return true; }

    public function rules(): array
    {
        return [
            'name' => 'nullable',
        ];
    }
}
