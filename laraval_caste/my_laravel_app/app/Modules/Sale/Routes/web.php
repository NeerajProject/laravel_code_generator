<?php

use Illuminate\Support\Facades\Route;

use App\Modules\Sale\Controller\SaleOrderController;
use App\Modules\Sale\Controller\SaleOrderLineController;
use App\Modules\Sale\Controller\ResPartnerController;
use App\Modules\Sale\Controller\ProductProductController;

Route::resource('sale-orders', SaleOrderController::class)->names('sale.order')->parameters(['sale-orders' => 'record']);
Route::resource('sale-order-lines', SaleOrderLineController::class)->names('sale.order.line')->parameters(['sale-order-lines' => 'record']);
Route::resource('res-partners', ResPartnerController::class)->names('res.partner')->parameters(['res-partners' => 'record']);
Route::resource('product-products', ProductProductController::class)->names('product.product')->parameters(['product-products' => 'record']);
