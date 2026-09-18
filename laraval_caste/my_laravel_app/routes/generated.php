<?php

use Illuminate\Support\Facades\Route;

use App\Modules\Sale\Controller\SaleOrderController;
use App\Modules\Sale\Controller\SaleOrderLineController;

Route::resource('sale-orders', SaleOrderController::class)
    ->names('sale_order')
    ->parameters(['sale-orders' => 'record']);

Route::resource('sale-order-lines', SaleOrderLineController::class)
    ->names('sale_order_line')
    ->parameters(['sale-order-lines' => 'record']);
