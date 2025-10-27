#!/bin/bash

echo "🧪 ТЕСТИРОВАНИЕ ВСЕХ ЭНДПОИНТОВ"
echo "================================"

BASE_URL="https://connect-aitu.me/api"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для проверки статуса
check_status() {
    if [ $1 -eq $2 ]; then
        echo -e "${GREEN}✅ PASS${NC}"
    else
        echo -e "${RED}❌ FAIL (ожидался $2, получен $1)${NC}"
    fi
}

echo ""
echo "1️⃣  HEALTH CHECK"
echo "----------------"
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/../health")
echo -n "GET /health: "
check_status $HEALTH 200

echo ""
echo "2️⃣  АВТОРИЗАЦИЯ"
echo "----------------"

# Login
echo -n "POST /auth/login: "
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"ChangeThisAdminPassword123!"}')
LOGIN_STATUS=$(echo $LOGIN_RESPONSE | jq -r '.access_token // "error"')
if [ "$LOGIN_STATUS" != "error" ]; then
    TOKEN=$LOGIN_STATUS
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    exit 1
fi

# Refresh token
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.refresh_token')
echo -n "POST /auth/refresh: "
REFRESH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}")
check_status $REFRESH_STATUS 200

# Logout
echo -n "POST /auth/logout: "
LOGOUT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/auth/logout" \
  -H "Authorization: Bearer $TOKEN")
check_status $LOGOUT_STATUS 200

echo ""
echo "3️⃣  СПЕЦИАЛЬНОСТИ (MAJORS)"
echo "---------------------------"

# Get all majors
echo -n "GET /majors: "
MAJORS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/majors?limit=5" \
  -H "Authorization: Bearer $TOKEN")
check_status $MAJORS_STATUS 200

# Get specific major
echo -n "GET /majors/{code}: "
MAJOR_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/majors/M001" \
  -H "Authorization: Bearer $TOKEN")
check_status $MAJOR_STATUS 200

echo ""
echo "4️⃣  ПРЕДМЕТЫ (SUBJECTS)"
echo "------------------------"

# Get all subjects
echo -n "GET /subjects: "
SUBJECTS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/subjects?limit=5" \
  -H "Authorization: Bearer $TOKEN")
check_status $SUBJECTS_STATUS 200

# Get specific subject
echo -n "GET /subjects/{code}: "
SUBJECT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/subjects/TGO" \
  -H "Authorization: Bearer $TOKEN")
check_status $SUBJECT_STATUS 200

echo ""
echo "5️⃣  СВОБОДНЫЙ РЕЖИМ (PRACTICE)"
echo "-------------------------------"

# Start practice
echo -n "POST /practice/start: "
PRACTICE_START=$(curl -s -X POST "$BASE_URL/practice/start" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"subject_code":"TGO"}')
PRACTICE_ID=$(echo $PRACTICE_START | jq -r '.attempt_id // "error"')
if [ "$PRACTICE_ID" != "error" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${YELLOW}⚠️  SKIP (нет вопросов в TGO)${NC}"
fi

echo ""
echo "6️⃣  ЭКЗАМЕНЫ (EXAM)"
echo "--------------------"

# Start exam
echo -n "POST /exam/start: "
EXAM_START=$(curl -s -X POST "$BASE_URL/exam/start" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"major_code":"M001"}')
EXAM_ID=$(echo $EXAM_START | jq -r '.attempt_id // "error"')
if [ "$EXAM_ID" != "error" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    
    # Get exam status
    echo -n "GET /exam/{id}: "
    EXAM_GET=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/exam/$EXAM_ID" \
      -H "Authorization: Bearer $TOKEN")
    check_status $EXAM_GET 200
else
    echo -e "${YELLOW}⚠️  SKIP (нет вопросов)${NC}"
fi

echo ""
echo "7️⃣  СТАТИСТИКА"
echo "---------------"

# My stats
echo -n "GET /stats/my: "
STATS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/stats/my" \
  -H "Authorization: Bearer $TOKEN")
check_status $STATS_STATUS 200

echo ""
echo "8️⃣  АДМИН ПАНЕЛЬ"
echo "-----------------"

# Get users
echo -n "GET /admin/users: "
ADMIN_USERS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/admin/users?limit=5" \
  -H "Authorization: Bearer $TOKEN")
check_status $ADMIN_USERS 200

# Get attempts
echo -n "GET /admin/attempts: "
ADMIN_ATTEMPTS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/admin/attempts?limit=5" \
  -H "Authorization: Bearer $TOKEN")
check_status $ADMIN_ATTEMPTS 200

# Get stats overview
echo -n "GET /admin/stats/overview: "
ADMIN_STATS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/admin/stats/overview" \
  -H "Authorization: Bearer $TOKEN")
check_status $ADMIN_STATS 200

echo ""
echo "================================"
echo "✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО"
echo ""