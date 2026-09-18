<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create(
            'sale_orders',
            function (Blueprint $table) {

                $table->id();

            $table->string('name');
            $table->foreignId('customer_id')->nullable()->constrained()->nullOnDelete();
            $table->decimal('amount_total', 15, 2)->nullable();

                $table->timestamps();

            }
        );
    }

    public function down(): void
    {
        Schema::dropIfExists(
            'sale_orders'
        );
    }
};
