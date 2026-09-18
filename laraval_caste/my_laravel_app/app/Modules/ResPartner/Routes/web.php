<?php
use Illuminate\Support\Facades\Route;
use App\Modules\ResPartner\Controller\ResPartnerController;

Route::resource('customers', ResPartnerController::class)->names('res.partner');
