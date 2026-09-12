# Required safety step before applying this package

The previous Compose file stored PostgreSQL data only in the container writable layer. The corrected configuration adds a named persistent volume. **Back up the existing database before replacing or recreating the PostgreSQL container.**

From the original project directory, while the old Compose file is still present:

```powershell
New-Item -ItemType Directory -Force .\backups | Out-Null
docker start postgres
Start-Sleep -Seconds 10
docker exec postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f /tmp/fraud-db.dump'
docker cp postgres:/tmp/fraud-db.dump .\backups\fraud-db-before-upgrade.dump
Get-Item .\backups\fraud-db-before-upgrade.dump
```

Do not continue unless the final command shows a non-zero-size backup file.
