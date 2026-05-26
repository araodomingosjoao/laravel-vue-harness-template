<?php

declare(strict_types=1);

namespace App\Providers;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\ServiceProvider;

final class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        //
    }

    public function boot(): void
    {
        // Strict mode em ambiente local apanha bugs cedo
        Model::shouldBeStrict(! $this->app->isProduction());

        // Prevent N+1 em desenvolvimento — exception em vez de query silenciosa
        Model::preventLazyLoading(! $this->app->isProduction());
    }
}
