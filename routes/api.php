<?php

declare(strict_types=1);

use App\Http\Controllers\Api\PingController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

Route::get('/ping', PingController::class);

// Adiciona aqui os endpoints do teu projecto.
// Convenção: agrupar por prefixo, usar Resource Controllers,
// validar com Form Requests, devolver com API Resources.
