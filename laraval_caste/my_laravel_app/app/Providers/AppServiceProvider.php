<?php

namespace App\Providers;

use Illuminate\Support\Facades\Vite;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        $this->app->bind(\App\Modules\Accounting\Repository\ResPartnerRepositoryInterface::class, \App\Modules\Accounting\Repository\ResPartnerRepository::class);
        $this->app->bind(\App\Modules\Sale\Repository\ResPartnerRepositoryInterface::class, \App\Modules\Sale\Repository\ResPartnerRepository::class);
        $this->app->bind(\App\Modules\Sale\Repository\SaleOrderRepositoryInterface::class, \App\Modules\Sale\Repository\SaleOrderRepository::class);
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        Vite::prefetch(concurrency: 3);
    }
}
