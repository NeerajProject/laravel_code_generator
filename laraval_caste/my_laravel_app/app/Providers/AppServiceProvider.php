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
        $this->app->bind(\App\Modules\OrderLine\Repository\OrderLineRepositoryInterface::class, \App\Modules\OrderLine\Repository\OrderLineRepository::class);
        $this->app->bind(\App\Modules\ResPartner\Repository\ResPartnerRepositoryInterface::class, \App\Modules\ResPartner\Repository\ResPartnerRepository::class);
        $this->app->bind(\App\Modules\SaleOrder\Repository\SaleOrderRepositoryInterface::class, \App\Modules\SaleOrder\Repository\SaleOrderRepository::class);
        //
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        Vite::prefetch(concurrency: 3);
    }
}
