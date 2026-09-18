<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('sale_order_lines', function (Blueprint $table) {
            $table->id();
            $table->foreignId('order_id')->nullable()->constrained('sale_orders')->nullOnDelete();
            $table->foreignId('product_id')->nullable()->constrained('product_products')->nullOnDelete();
            $table->decimal('quantity', 16, 4)->default(0);
            $table->decimal('unit_price', 16, 4)->default(0);
            $table->decimal('subtotal', 16, 4)->default(0);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('sale_order_lines');
    }
};
