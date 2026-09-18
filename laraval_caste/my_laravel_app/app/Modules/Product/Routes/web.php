<?php

use Illuminate\Support\Facades\Route;
use App\Modules\Product\Controller\ProductProductController;

Route::resource('products', ProductProductController::class)->names('product.product');
