<?php

namespace App\Modules\Project\Request;

use Illuminate\Foundation\Http\FormRequest;

class ProjectTaskRequest extends FormRequest
{
    public function authorize(): bool { return true; }

    public function rules(): array
    {
        return [
            'name' => 'required',
            'project_id' => 'nullable',
            'assignee_id' => 'nullable',
            'deadline' => 'nullable',
            'state' => 'nullable',
            'description' => 'nullable',
        ];
    }
}
