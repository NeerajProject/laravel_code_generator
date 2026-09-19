<?php

namespace App\Modules\Project\Request;

use Illuminate\Foundation\Http\FormRequest;

class ProjectTimesheetRequest extends FormRequest
{
    public function authorize(): bool { return true; }

    public function rules(): array
    {
        return [
            'date' => 'required',
            'task_id' => 'nullable',
            'employee_id' => 'nullable',
            'description' => 'nullable',
            'hours' => 'required',
        ];
    }
}
