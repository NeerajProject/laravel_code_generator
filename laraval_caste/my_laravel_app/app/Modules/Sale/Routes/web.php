<?php

use Illuminate\Support\Facades\Route;
use App\Modules\Sale\Controller\SaleOrderController;

Route::resource('sale-order-lines', SaleOrderController::class)->names('sale.order');
