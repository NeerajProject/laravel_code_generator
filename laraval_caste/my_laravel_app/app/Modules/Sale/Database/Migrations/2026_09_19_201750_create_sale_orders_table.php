<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('sale_orders', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->foreignId('customer_id')->nullable()->constrained('res_partners')->nullOnDelete();
            $table->date('order_date')->nullable();
            $table->string('state', 50)->nullable();
            $table->decimal('amount_total', 16, 4)->default(0);
            $table->text('note')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('sale_orders');
    }
};
