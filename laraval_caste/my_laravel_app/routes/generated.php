<?php

use Illuminate\Support\Facades\Route;

// --- Sale Module Controllers ---
use App\Modules\Sale\Controller\SaleOrderController;
use App\Modules\Sale\Controller\SaleOrderLineController;
use App\Modules\Sale\Controller\ResPartnerController;
use App\Modules\Sale\Controller\ProductProductController;

// --- Project Module Controllers ---
use App\Modules\Project\Controller\ProjectProjectController;
use App\Modules\Project\Controller\ProjectTaskController;
use App\Modules\Project\Controller\ProjectTimesheetController;
use App\Modules\Project\Controller\ResUsersController;
use App\Modules\Project\Controller\HrEmployeeController;


// ==========================================
// SALE MODULE ROUTES
// ==========================================

Route::resource('sale-orders', SaleOrderController::class)
    ->names('sale_order')
    ->parameters(['sale-orders' => 'record']);

Route::resource('sale-order-lines', SaleOrderLineController::class)
    ->names('sale_order_line')
    ->parameters(['sale-order-lines' => 'record']);

Route::resource('res-partners', ResPartnerController::class)
    ->names('res_partner')
    ->parameters(['res-partners' => 'record']);

Route::resource('product-products', ProductProductController::class)
    ->names('product_product')
    ->parameters(['product-products' => 'record']);


// ==========================================
// PROJECT MODULE ROUTES
// ==========================================

Route::resource('projects', ProjectProjectController::class)
    ->names('project_project')
    ->parameters(['projects' => 'record']);

Route::resource('project-tasks', ProjectTaskController::class)
    ->names('project_task')
    ->parameters(['project-tasks' => 'record']);

Route::resource('project-timesheets', ProjectTimesheetController::class)
    ->names('project_timesheet')
    ->parameters(['project-timesheets' => 'record']);

// Optional Dependency Routes (Users & Employees)
Route::resource('res-users', ResUsersController::class)
    ->names('res_users')
    ->parameters(['res-users' => 'record']);

Route::resource('hr-employees', HrEmployeeController::class)
    ->names('hr_employee')
    ->parameters(['hr-employees' => 'record']);
