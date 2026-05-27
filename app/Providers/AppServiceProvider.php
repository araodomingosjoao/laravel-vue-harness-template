<?php

declare(strict_types=1);

namespace App\Providers;

use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\ServiceProvider;

final class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        //
    }

    public function boot(): void
    {
        RateLimiter::for('api', fn (Request $r) => Limit::perMinute(60)->by($r->user()?->id ?: $r->ip()));

        // Strict mode em ambiente local apanha bugs cedo
        Model::shouldBeStrict(! $this->app->isProduction());

        // Prevent N+1 em desenvolvimento — exception em vez de query silenciosa
        Model::preventLazyLoading(! $this->app->isProduction());
    }
}
