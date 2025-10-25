#!/bin/bash

# ===================================
# SSL Certificate Setup for PRODUCTION
# ===================================

set -e

# Берем домен из .env файла
DOMAIN=$(grep DOMAIN .env | cut -d '=' -f2)
EMAIL=$(grep LETSENCRYPT_EMAIL .env | cut -d '=' -f2)

echo "🔒 Получение SSL сертификата для $DOMAIN"
echo "============================================"
echo ""

echo "📋 Шаг 1: Подготовка окружения"

# Создаем необходимые папки
mkdir -p nginx/conf.d
mkdir -p data/certbot/conf
mkdir -p data/certbot/www

# Создаем основную конфигурацию Nginx если её нет
if [ ! -f nginx/nginx.conf ]; then
    echo "📝 Создание nginx/nginx.conf..."
    cat > nginx/nginx.conf << 'NGINX_EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/conf.d/*.conf;
}
NGINX_EOF
fi

echo "📋 Шаг 2: Создание временной конфигурации для получения сертификата"

# Бэкапим основную конфигурацию если она существует
if [ -f nginx/conf.d/connect-aitu.conf ]; then
    echo "💾 Создание бэкапа основной конфигурации..."
    cp nginx/conf.d/connect-aitu.conf nginx/conf.d/connect-aitu.conf.bak
fi

# Создаем временную конфигурацию для получения сертификата
cat > nginx/conf.d/connect-aitu.conf << 'TEMP_EOF'
server {
    listen 80;
    listen [::]:80;
    server_name _;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'SSL Certificate Setup in progress...';
        add_header Content-Type text/plain;
    }
}
TEMP_EOF

echo "✅ Временная конфигурация создана"
echo ""

echo "📋 Шаг 3: Перезапуск Nginx с временной конфигурацией"
docker-compose -f docker-compose.prod.yml stop nginx 2>/dev/null || true
docker-compose -f docker-compose.prod.yml up -d nginx
sleep 5

# Проверяем что nginx запустился
if docker-compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
    echo "✅ Nginx успешно запущен"
else
    echo "❌ Nginx не запустился. Проверьте логи: docker-compose -f docker-compose.prod.yml logs nginx"
    exit 1
fi

echo ""

echo "📋 Шаг 4: Получение сертификата от Let's Encrypt"
echo "⏳ Это может занять несколько минут..."
if docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN; then
    echo "✅ Сертификат успешно получен!"
else
    echo "❌ Ошибка при получении сертификата"
    echo "Проверьте что:"
    echo "  1. Домен $DOMAIN указывает на IP этого сервера"
    echo "  2. Порт 80 открыт в фаерволе"
    echo "  3. Nginx доступен извне"
    exit 1
fi

echo ""

echo "📋 Шаг 5: Восстановление основной конфигурации"
# Удаляем временную конфигурацию
rm -f nginx/conf.d/connect-aitu.conf

# Восстанавливаем основную из бэкапа
if [ -f nginx/conf.d/connect-aitu.conf.bak ]; then
    mv nginx/conf.d/connect-aitu.conf.bak nginx/conf.d/connect-aitu.conf
    echo "✅ Основная конфигурация восстановлена из бэкапа"
else
    echo "📝 Создание стандартной конфигурации с SSL"
    cat > nginx/conf.d/connect-aitu.conf << 'SSL_EOF'
server {
    listen 80;
    listen [::]:80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name _;

    ssl_certificate /etc/letsencrypt/live/connect-aitu.me/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/connect-aitu.me/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://backend:8000/health;
        access_log off;
    }

    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
SSL_EOF
fi

echo "✅ Конфигурация восстановлена"
echo ""

echo "📋 Шаг 6: Финальный перезапуск Nginx с SSL"
docker-compose -f docker-compose.prod.yml restart nginx
sleep 3

echo "✅ Nginx перезапущен с SSL"
echo ""

echo "🎉 ГОТОВО!"
echo ""
echo "✅ SSL сертификат успешно установлен"
echo "✅ Сайт доступен по адресу: https://$DOMAIN"
echo ""
echo "📝 Примечания:"
echo "   - Сертификат будет автоматически обновляться"
echo "   - Проверить статус: docker-compose -f docker-compose.prod.yml logs certbot"
echo "   - Проверить сайт: curl -I https://$DOMAIN"
echo ""
