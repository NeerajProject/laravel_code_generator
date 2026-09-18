<?php

namespace App\Modules\Project\Request;

use Illuminate\Foundation\Http\FormRequest;

class ProjectProjectRequest extends FormRequest
{
    public function authorize(): bool { return true; }

    public function rules(): array
    {
        return [
            'name' => 'required|string|max:255',
            'code' => 'nullable|string|max:255',
            'description' => 'nullable|string',
            'is_active' => 'nullable|boolean',
            'task_ids' => 'nullable|array',
            'task_ids.*.name' => 'nullable|string|max:255',
            'task_ids.*.description' => 'nullable|string|max:255',
            'task_ids.*.is_done' => 'nullable|boolean',
        ];
    }
}
