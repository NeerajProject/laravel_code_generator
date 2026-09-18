<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        if (!Schema::hasTable('project_tasks')) {
            Schema::create('project_tasks', function (Blueprint $table) {
                $table->id();
                $table->foreignId('project_project_id')->nullable()->constrained('project_projects')->cascadeOnDelete();
                $table->string('name')->nullable();
                $table->text('description')->nullable();
                $table->boolean('is_done')->default(false);
                $table->timestamps();
            });
        }
    }

    public function down(): void {
        Schema::dropIfExists('project_tasks');
    }
};
