#!/bin/bash
# backup/backup.sh
# Sauvegarde PostgreSQL de CloudApp, executee dans la pile de production (service "backup").
#
# Modes :
#   run     (defaut) sauvegarde immediate, verification, puis une sauvegarde toutes les
#           BACKUP_INTERVAL_SECONDS secondes (86400 = une par jour)
#   once    une seule sauvegarde (controle d'integrite + rotation)
#   verify  restaure la derniere sauvegarde dans une base temporaire et compare le nombre de lignes
#           de chaque table avec la base de production, puis supprime la base temporaire
#
# Variables (fournies par docker-compose.prod.yml) :
#   PGHOST, PGUSER, PGPASSWORD, PGDATABASE     connexion a PostgreSQL
#   BACKUP_DIR (defaut /backups)               dossier des sauvegardes (volume)
#   BACKUP_KEEP_DAYS (defaut 7)                duree de conservation
#   BACKUP_INTERVAL_SECONDS (defaut 86400)     intervalle entre deux sauvegardes
#
# Restauration manuelle d'une sauvegarde dans la base de production :
#   gunzip -c /backups/<fichier>.sql.gz | psql -v ON_ERROR_STOP=1 -d "$PGDATABASE"

set -euo pipefail

MODE="${1:-run}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
BACKUP_KEEP_DAYS="${BACKUP_KEEP_DAYS:-7}"
BACKUP_INTERVAL_SECONDS="${BACKUP_INTERVAL_SECONDS:-86400}"
PGDATABASE="${PGDATABASE:-cloudapp_db}"
export PGDATABASE
SCRATCH_DB="restore_check"

log() { echo "[backup] $(date -u +%Y-%m-%dT%H:%M:%SZ) $*"; }

wait_for_db() {
  local i
  for i in $(seq 1 60); do
    if pg_isready -q; then return 0; fi
    sleep 2
  done
  log "ERREUR : PostgreSQL ne repond pas apres 120 s"
  return 1
}

do_backup() {
  mkdir -p "$BACKUP_DIR"
  wait_for_db
  local stamp file
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  file="$BACKUP_DIR/cloudapp_db_${stamp}.sql.gz"

  pg_dump --no-owner --clean --if-exists "$PGDATABASE" | gzip -9 > "$file.tmp"
  gzip -t "$file.tmp"                       # controle d'integrite de l'archive
  if [ ! -s "$file.tmp" ]; then
    log "ERREUR : sauvegarde vide"
    rm -f "$file.tmp"
    return 1
  fi
  mv "$file.tmp" "$file"
  log "OK sauvegarde creee : $file ($(du -h "$file" | cut -f1))"

  # Rotation : supprime les sauvegardes plus anciennes que BACKUP_KEEP_DAYS jours
  find "$BACKUP_DIR" -name 'cloudapp_db_*.sql.gz' -mtime +"$BACKUP_KEEP_DAYS" -print -delete \
    | sed 's/^/[backup] supprime (rotation) : /' || true
}

# Nombre de lignes par table (schema public), un resultat par ligne : "table|nombre"
row_counts() {
  local db="$1" sql
  sql="$(psql -At -d "$db" -c "SELECT COALESCE(string_agg(format('SELECT %L AS t, count(*) AS n FROM %I', tablename, tablename), ' UNION ALL '), 'SELECT ''-'' AS t, 0 AS n') FROM pg_tables WHERE schemaname = 'public'")"
  psql -At -F '|' -d "$db" -c "SELECT * FROM ($sql) s ORDER BY t"
}

do_verify() {
  local latest
  latest="$(ls -1t "$BACKUP_DIR"/cloudapp_db_*.sql.gz 2>/dev/null | head -n 1 || true)"
  if [ -z "$latest" ]; then
    log "ERREUR : aucune sauvegarde a verifier"
    return 1
  fi
  wait_for_db
  log "verification de $latest"

  # Restauration reelle dans une base temporaire : ON_ERROR_STOP fait echouer la moindre erreur SQL.
  dropdb --if-exists "$SCRATCH_DB"
  createdb "$SCRATCH_DB"
  if ! gunzip -c "$latest" | psql -q -v ON_ERROR_STOP=1 -d "$SCRATCH_DB" > /dev/null; then
    log "ERREUR : la restauration de $latest a echoue"
    dropdb --if-exists "$SCRATCH_DB"
    return 1
  fi

  local prod restored status=0 ahead=0 t n r
  prod="$(row_counts "$PGDATABASE")"
  restored="$(row_counts "$SCRATCH_DB")"
  dropdb "$SCRATCH_DB"

  if [ "$(echo "$prod" | wc -l)" != "$(echo "$restored" | wc -l)" ]; then
    log "ERREUR : la liste des tables restaurees differe de la production"
    status=1
  fi

  log "lignes par table (restaurees / production) :"
  while IFS='|' read -r t n; do
    r="$(echo "$restored" | awk -F'|' -v t="$t" '$1==t {print $2}')"
    if [ -z "$r" ]; then
      log "  $t : ABSENTE de la base restauree"
      status=1
    elif [ "$r" -gt "$n" ]; then
      log "  $t : $r / $n  <- ERREUR : plus de lignes restaurees qu'en production"
      status=1
    else
      log "  $t : $r / $n"
      if [ "$r" -lt "$n" ]; then ahead=$((ahead + n - r)); fi
    fi
  done <<< "$prod"

  if [ "$status" -ne 0 ]; then
    log "VERIFICATION ECHEC"
    return 1
  fi
  if [ "$ahead" -gt 0 ]; then
    log "VERIFICATION OK : la sauvegarde se restaure ($ahead ligne(s) ecrite(s) en production depuis la sauvegarde)"
  else
    log "VERIFICATION OK : la sauvegarde se restaure et les donnees sont identiques"
  fi
}

case "$MODE" in
  once)
    do_backup
    ;;
  verify)
    do_verify
    ;;
  run)
    log "demarrage : une sauvegarde toutes les ${BACKUP_INTERVAL_SECONDS} s, conservation ${BACKUP_KEEP_DAYS} jours"
    while true; do
      do_backup
      do_verify
      sleep "$BACKUP_INTERVAL_SECONDS"
    done
    ;;
  *)
    echo "Usage : backup.sh [run|once|verify]" >&2
    exit 2
    ;;
esac
