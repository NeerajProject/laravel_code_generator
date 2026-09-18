<?php
use Illuminate\Support\Facades\Route;
use App\Modules\OrderLine\Controller\OrderLineController;

Route::resource('sales/order-lines', OrderLineController::class)->names('order.line');
