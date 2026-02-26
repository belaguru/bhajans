# 🔄 Automated Backups - Belaguru Portal

## Overview

✅ **Automated daily backups** of your database  
✅ **7-day retention** (keeps last 7 days of backups)  
✅ **Easy recovery** if anything goes wrong  
✅ **Systemd timer** runs automatically  

---

## 📋 How It Works

### Backup Schedule
- **Time:** Daily at 2:00 AM IST (configurable)
- **Location:** `/home/kreddy/.belaguru/backups/`
- **Format:** `portal_YYYYMMDD_HHMMSS.db`
- **Retention:** Last 7 days (older files auto-deleted)
- **Size:** ~20KB per backup

### Automatic Process
```
Every day at 2:00 AM:
  1. Stop backup timer
  2. Copy database to backups folder
  3. Verify backup is valid
  4. Delete backups older than 7 days
  5. Log result to backup.log
```

---

## 🔍 Check Backup Status

### View Timer Status
```bash
systemctl --user status belaguru-backup.timer
```

### See Next Scheduled Backup
```bash
systemctl --user list-timers belaguru-backup.timer
```

### View All Backups
```bash
ls -lh /home/kreddy/.belaguru/backups/
```

### View Backup Log
```bash
cat /home/kreddy/.belaguru/backup.log
```

---

## 💾 Restore from Backup

### List Available Backups
```bash
/home/kreddy/Projects/belaguru-portal/scripts/restore.sh
```

Output:
```
Available backups:
/home/kreddy/.belaguru/backups/portal_20260226_092815.db (20K)
/home/kreddy/.belaguru/backups/portal_20260225_020000.db (20K)
...
```

### Restore Specific Backup
```bash
/home/kreddy/Projects/belaguru-portal/scripts/restore.sh 20260226_092815
```

**What happens:**
1. ✅ Current database is backed up (just in case)
2. ✅ Server is stopped gracefully
3. ✅ Database restored from backup
4. ✅ Server automatically restarted
5. ✅ Restore logged

---

## 🛠️ Manual Backup (Anytime)

Run a backup immediately:
```bash
/home/kreddy/Projects/belaguru-portal/scripts/backup.sh
```

This creates a backup regardless of the schedule.

---

## ⚙️ Configuration

### Change Backup Time
Edit: `/home/keddy/.config/systemd/user/belaguru-backup.timer`

Change this line to desired time:
```ini
OnCalendar=*-*-* 02:00:00
```

Examples:
- `*-*-* 00:00:00` — Midnight
- `*-*-* 06:00:00` — 6:00 AM
- `*-*-* 12:00:00` — Noon
- `*-*-* 18:00:00` — 6:00 PM

Then reload:
```bash
systemctl --user daemon-reload
systemctl --user restart belaguru-backup.timer
```

### Change Retention (Keep More/Less Days)
Edit: `/home/kreddy/Projects/belaguru-portal/scripts/backup.sh`

Change this line:
```bash
RETENTION_DAYS=7
```

Examples:
- `RETENTION_DAYS=30` — Keep 30 days
- `RETENTION_DAYS=3` — Keep 3 days

---

## 📊 Backup Status

Current backups:
```bash
$ ls -lh /home/kreddy/.belaguru/backups/
-rw-r--r-- 1 kreddy kreddy 20K Feb 26 09:28 portal_20260226_092815.db
-rw-r--r-- 1 kreddy kreddy 20K Feb 26 09:28 portal_20260226_092808.db
```

Timer status:
```
✅ Loaded: loaded
✅ Active: active (waiting)
✅ Trigger: Fri 2026-02-27 00:00:00 IST
```

---

## 🚨 Disaster Recovery Checklist

If database gets corrupted or deleted:

1. **List backups:**
   ```bash
   /home/kreddy/Projects/belaguru-portal/scripts/restore.sh
   ```

2. **Choose most recent backup:**
   ```bash
   /home/kreddy/Projects/belaguru-portal/scripts/restore.sh 20260226_092815
   ```

3. **Confirm restore** (you'll be prompted)

4. **Verify data is restored:**
   ```bash
   curl http://localhost:8000/api/stats
   ```

5. **Check portal in browser:**
   ```
   http://34.93.110.163:8000
   ```

---

## 📈 What's Backed Up

✅ **All bhajans** (titles, lyrics, tags)  
✅ **All user data** (upload dates, names)  
✅ **Soft-deleted bhajans** (hidden but recoverable)  

---

## 🔐 Security Notes

- Backups stored locally on same VM
- No encryption (backups are plaintext SQLite)
- For critical production, consider:
  - Remote backups (cloud storage)
  - Encrypted backups
  - Off-site storage

---

## ✅ System Health Check

```bash
# Everything healthy?
echo "Checking backup system..."
systemctl --user status belaguru-backup.timer | grep Active
ls /home/kreddy/.belaguru/backups/ | wc -l
tail -1 /home/kreddy/.belaguru/backup.log
```

Expected output:
```
Active: active (waiting)
2
[2026-02-26 09:28:15] Backup successful: ...
```

---

## 📞 Troubleshooting

### Timer Not Running
```bash
systemctl --user enable belaguru-backup.timer
systemctl --user start belaguru-backup.timer
```

### Backups Not Created
```bash
# Run manually to see errors
/home/kreddy/Projects/belaguru-portal/scripts/backup.sh
```

### Restore Failed
```bash
# Current DB is backed up before restore
ls /home/kreddy/.belaguru/backups/ | grep before_restore
```

---

## 📝 Log Files

**Backup log:**
```
/home/kreddy/.belaguru/backup.log
```

**Systemd log:**
```bash
journalctl --user -u belaguru-backup.service
```

---

## ✨ Summary

- ✅ Daily automatic backups (2:00 AM)
- ✅ 7-day retention (auto-cleanup)
- ✅ One-command restore
- ✅ Server stops/restarts automatically
- ✅ Logged and monitored
- ✅ **Your data is now protected**

---

**You will never lose data to a careless mistake again.** 🔒
