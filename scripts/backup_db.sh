#!/bin/bash
# 세라피나 MySQL 일일 자동 백업
# - tarot_mysql 컨테이너에 docker exec로 mysqldump
# - MYSQL_PWD 환경변수로 비밀번호 주입 (ps에서 안 보이게)
# - 14일 이상 된 백업 자동 정리
# - cron 호환 (PATH 명시)

set -e

# crontab 환경에서 PATH 보장 (cron은 최소 PATH라 docker 못 찾을 수 있음)
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$HOME/serapina-backups"
RETENTION_DAYS=14

cd "$PROJECT_DIR"

# .env에서 MYSQL_ROOT_PASSWORD / MYSQL_DATABASE 로드 (KEY=VALUE 줄을 export)
set -a
source .env
set +a

mkdir -p "$BACKUP_DIR"
TS=$(date +%Y%m%d_%H%M%S)
FILE="$BACKUP_DIR/tarot_chat_${TS}.sql.gz"

# mysqldump (gzip 압축, single-transaction으로 락 최소화)
docker exec -e MYSQL_PWD="$MYSQL_ROOT_PASSWORD" tarot_mysql \
  mysqldump -u root --single-transaction --quick --routines --triggers "$MYSQL_DATABASE" 2>/dev/null \
  | gzip > "$FILE"

# 빈 파일이면 실패로 처리
if [ ! -s "$FILE" ]; then
  echo "[$(date '+%F %T')] ❌ Backup FAILED — empty file" >&2
  rm -f "$FILE"
  exit 1
fi

# 오래된 백업 삭제 ($RETENTION_DAYS일 이상)
find "$BACKUP_DIR" -name "tarot_chat_*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

SIZE=$(du -h "$FILE" | cut -f1)
echo "[$(date '+%F %T')] ✅ Backup OK — $FILE ($SIZE)"
