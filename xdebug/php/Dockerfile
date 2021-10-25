FROM wordpress:php7.4-fpm

RUN docker-php-ext-install pdo pdo_mysql
RUN pecl install xdebug && docker-php-ext-enable xdebug
# RUN apt-get update && apt-get install -y libzip-dev zlib1g-dev libpq-dev mariadb-client unzip \
#   curl \
#   libmemcached-dev \
#   libz-dev \
#   libjpeg-dev \
#   libpng-dev \
#   libfreetype6-dev \
#   libssl-dev \
#   libmcrypt-dev \
#   libmagickwand-dev --no-install-recommends

# RUN pecl install imagick && \
#   docker-php-ext-enable imagick

# RUN docker-php-ext-install gd && \
#   docker-php-ext-configure gd --with-jpeg --with-freetype && \
#   docker-php-ext-install gd
