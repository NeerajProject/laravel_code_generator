<?php

use Illuminate\Support\Facades\Route;
use App\Modules\Project\Controller\ProjectProjectController;

Route::resource('tasks', ProjectProjectController::class)->names('project.project');
