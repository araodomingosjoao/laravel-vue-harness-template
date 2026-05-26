FROM php:8.4-cli-alpine

RUN apk add --no-cache \
    git \
    unzip \
    libzip-dev \
    icu-dev \
    oniguruma-dev \
    postgresql-dev \
    postgresql-client \
    nodejs \
    npm \
    && docker-php-ext-install \
       pdo \
       pdo_pgsql \
       bcmath \
       intl \
       mbstring \
       zip

# Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www

# Composer install corre quando o container arranca (em vez de no build)
# para permitir hot-reload sem rebuild.
CMD ["sh", "-c", "composer install --no-interaction && php artisan serve --host=0.0.0.0 --port=8000"]