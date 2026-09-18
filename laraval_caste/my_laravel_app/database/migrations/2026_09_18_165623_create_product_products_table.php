<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('product_products', function (Blueprint $table) {$table->id();
            $table->string('name');
            $table->string('code')->nullable();
            $table->decimal('list_price', 15, 2)->nullable();
            $table->decimal('standard_price', 15, 2)->nullable();
            $table->text('description')->nullable();
            $table->boolean('is_active')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void {
        Schema::dropIfExists('product_products');
    }
};
