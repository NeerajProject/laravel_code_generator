<?php

namespace App\Modules\Project\Request;

use Illuminate\Foundation\Http\FormRequest;

class ProjectProjectRequest extends FormRequest
{
    public function authorize(): bool { return true; }

    public function rules(): array
    {
        return [
            'name' => 'required',
            'manager_id' => 'nullable',
            'start_date' => 'nullable',
            'end_date' => 'nullable',
            'state' => 'nullable',
            'description' => 'nullable',
        ];
    }
}
