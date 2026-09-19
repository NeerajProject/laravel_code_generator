<?php

use Illuminate\Support\Facades\Route;

use App\Modules\Project\Controller\ProjectProjectController;
use App\Modules\Project\Controller\ProjectTaskController;
use App\Modules\Project\Controller\ProjectTimesheetController;
use App\Modules\Project\Controller\ResUsersController;
use App\Modules\Project\Controller\HrEmployeeController;

Route::resource('projects', ProjectProjectController::class)->names('project.project')->parameters(['projects' => 'record']);
Route::resource('project-tasks', ProjectTaskController::class)->names('project.task')->parameters(['project-tasks' => 'record']);
Route::resource('project-timesheets', ProjectTimesheetController::class)->names('project.timesheet')->parameters(['project-timesheets' => 'record']);
Route::resource('res-users', ResUsersController::class)->names('res.users')->parameters(['res-users' => 'record']);
Route::resource('hr-employees', HrEmployeeController::class)->names('hr.employee')->parameters(['hr-employees' => 'record']);
