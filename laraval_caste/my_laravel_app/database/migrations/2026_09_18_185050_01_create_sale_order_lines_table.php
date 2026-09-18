<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        if (!Schema::hasTable('sale_order_lines')) {
            Schema::create('sale_order_lines', function (Blueprint $table) {
                $table->id();
                $table->foreignId('sale_order_id')->nullable()->constrained('sale_orders')->cascadeOnDelete();
                $table->string('name')->nullable();
                $table->text('description')->nullable();
                $table->boolean('is_done')->default(false);
                $table->timestamps();
            });
        }
    }

    public function down(): void {
        Schema::dropIfExists('sale_order_lines');
    }
};
