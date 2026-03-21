#!/bin/bash
# Install nightly test cron job

SCRIPT_PATH="$HOME/Projects/belaguru-bhajans/run-nightly-tests.sh"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "run-nightly-tests.sh"; then
    echo "⚠️  Nightly test job already installed"
    echo ""
    echo "Current cron jobs:"
    crontab -l | grep "run-nightly-tests.sh"
    echo ""
    echo "To reinstall, first remove with:"
    echo "  crontab -l | grep -v 'run-nightly-tests.sh' | crontab -"
    exit 0
fi

# Add cron job (runs at 2:00 AM daily)
(crontab -l 2>/dev/null; echo "0 2 * * * $SCRIPT_PATH >> $HOME/Projects/belaguru-bhajans/test-reports/cron.log 2>&1") | crontab -

echo "✅ Nightly test job installed!"
echo ""
echo "Schedule: Every day at 2:00 AM"
echo "Script: $SCRIPT_PATH"
echo "Logs: ~/Projects/belaguru-bhajans/test-reports/"
echo ""
echo "To view current cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove:"
echo "  crontab -l | grep -v 'run-nightly-tests.sh' | crontab -"
