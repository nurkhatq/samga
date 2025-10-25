#!/bin/bash

# ===================================
# SSL Certificate Setup (Let's Encrypt)
# ===================================

set -e

DOMAIN="connect-aitu.me"
EMAIL="admin@connect-aitu.me"

echo "🔒 Получение SSL сертификата для $DOMAIN"
echo "============================================"
echo ""

# Проверка что docker-compose запущен
if ! docker-compose ps | grep -q "connect_aitu_nginx"; then
    echo "❌ Nginx не запущен!"
    echo "   Сначала запустите: docker-compose up -d nginx"
    exit 1
fi

echo "📋 Шаг 1: Создание временной конфигурации Nginx (HTTP only)"

# Создаем временную конфигурацию без SSL
cat > nginx/conf.d/connect-aitu-temp.conf << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name connect-aitu.me www.connect-aitu.me;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'Temporary page for SSL certificate generation';
        add_header Content-Type text/plain;
    }
}
EOF

# Удаляем основную конфигурацию временно
if [ -f nginx/conf.d/connect-aitu.conf ]; then
    mv nginx/conf.d/connect-aitu.conf nginx/conf.d/connect-aitu.conf.bak
fi

echo "✅ Временная конфигурация создана"
echo ""

echo "📋 Шаг 2: Перезапуск Nginx"
docker-compose restart nginx
sleep 3
echo "✅ Nginx перезапущен"
echo ""

echo "📋 Шаг 3: Получение сертификата от Let's Encrypt"
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d $DOMAIN \
    -d www.$DOMAIN

echo "✅ Сертификат получен"
echo ""

echo "📋 Шаг 4: Восстановление основной конфигурации"
# Удаляем временную
rm -f nginx/conf.d/connect-aitu-temp.conf

# Восстанавливаем основную
if [ -f nginx/conf.d/connect-aitu.conf.bak ]; then
    mv nginx/conf.d/connect-aitu.conf.bak nginx/conf.d/connect-aitu.conf
fi

echo "✅ Конфигурация восстановлена"
echo ""

echo "📋 Шаг 5: Финальный перезапуск Nginx с SSL"
docker-compose restart nginx
sleep 3
echo "✅ Nginx перезапущен с SSL"
echo ""

echo "🎉 ГОТОВО!"
echo ""
echo "✅ SSL сертификат успешно установлен"
echo "✅ Сайт доступен по адресу: https://$DOMAIN"
echo ""
echo "📝 Примечания:"
echo "   - Сертификат будет автоматически обновляться каждые 12 часов"
echo "   - Проверить статус: docker-compose logs certbot"
echo ""
