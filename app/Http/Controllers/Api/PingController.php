<?php

declare(strict_types=1);

namespace App\Http\Controllers\Api;

use Illuminate\Http\JsonResponse;

class PingController
{
    public function __invoke(): JsonResponse
    {
        return response()->json(['pong' => true]);
    }
}
