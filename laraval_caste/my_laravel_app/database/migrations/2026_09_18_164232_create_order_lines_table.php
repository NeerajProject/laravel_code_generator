<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('order_lines', function (Blueprint $table) {$table->id();
            $table->foreignId('order_id')->nullable();
            $table->string('product_name');
            $table->decimal('quantity', 15, 2)->nullable();
            $table->decimal('price_unit', 15, 2)->nullable();
            $table->decimal('subtotal', 15, 2)->nullable();
            $table->timestamps();
        });
    }
    public function down(): void {
        Schema::dropIfExists('order_lines');
    }
};
