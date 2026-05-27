<?php

declare(strict_types=1);

it('returns pong on GET /api/ping', function () {
    $this->getJson('/api/ping')
        ->assertOk()
        ->assertExactJson(['pong' => true]);
});

it('rejects non-GET methods on GET /api/ping', function () {
    $this->postJson('/api/ping')->assertStatus(405);
});
