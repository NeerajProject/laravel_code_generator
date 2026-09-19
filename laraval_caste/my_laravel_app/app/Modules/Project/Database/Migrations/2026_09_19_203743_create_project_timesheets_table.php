<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('project_timesheets', function (Blueprint $table) {
            $table->id();
            $table->date('date')->nullable();
            $table->foreignId('task_id')->nullable()->constrained('project_tasks')->nullOnDelete();
            $table->foreignId('employee_id')->nullable()->constrained('hr_employees')->nullOnDelete();
            $table->string('description')->nullable();
            $table->decimal('hours', 16, 4)->default(0);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('project_timesheets');
    }
};
