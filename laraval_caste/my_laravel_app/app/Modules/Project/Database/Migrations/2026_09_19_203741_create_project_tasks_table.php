<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('project_tasks', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->foreignId('project_id')->nullable()->constrained('project_projects')->nullOnDelete();
            $table->foreignId('assignee_id')->nullable()->constrained('res_users')->nullOnDelete();
            $table->date('deadline')->nullable();
            $table->string('state', 50)->nullable();
            $table->text('description')->nullable();
            $table->decimal('total_hours', 16, 4)->default(0);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('project_tasks');
    }
};
