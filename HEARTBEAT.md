# HEARTBEAT.md - DISABLED

# Heartbeat cycle has been disabled to prevent overnight API costs.
# 
# Previous issue: Background processes (Polymarket bot, etc.) accumulated context,
# triggering timeouts on agent turns. Each timeout = API call = $$$.
# 
# With 20+ failed calls/night @ 73% context = ~$7/night.
#
# To re-enable: Add tasks below and heartbeat will resume.
# Keep it minimal to avoid token accumulation.
