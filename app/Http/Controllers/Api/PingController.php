<?php

declare(strict_types=1);

namespace App\Http\Controllers\Api;

use Illuminate\Http\JsonResponse;

class PingController extends \App\Http\Controllers\Controller
{
    public function __invoke(): JsonResponse
    {
        return response()->json(['pong' => true]);
    }
}
