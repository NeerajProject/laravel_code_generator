<?php
use Illuminate\Support\Facades\Route;
use App\Modules\SaleOrder\Controller\SaleOrderController;

Route::resource('sales/orders', SaleOrderController::class)->names('sale.order');
Route::post('sales/orders/{id}/submit', [SaleOrderController::class, 'submit'])->name('sale.order.submit');
