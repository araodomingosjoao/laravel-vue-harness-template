<?php

declare(strict_types=1);
use App\Models\User;

it('responds to health check', function () {
    $this->get('/up')->assertOk();
});

it('returns authenticated user', function () {
    $user = User::factory()->create();

    $this->actingAs($user)
        ->getJson('/api/user')
        ->assertOk()
        ->assertJsonPath('email', $user->email);
});
