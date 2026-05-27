<?php

declare(strict_types=1);

it('returns pong on GET /api/ping', function () {
    $this->getJson('/api/ping')
        ->assertOk()
        ->assertExactJson(['pong' => true]);
});
