#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOBI_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$TOBI_DIR/presenterm_config.yaml"

if [[ "${CODESPACES:-}" != "true" ]]; then
  echo "Not in Codespaces; leaving $CONFIG_FILE unchanged"
  exit 0
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "presenterm config not found at $CONFIG_FILE; skipping Codespaces overrides"
  exit 0
fi

# Force-enable browser-safe snippet execute keybinding in Codespaces.
if grep -Eq '^[[:space:]]*execute_code:[[:space:]]*\[.*\]' "$CONFIG_FILE"; then
  sed -i -E 's|^([[:space:]]*execute_code:[[:space:]]*)\[.*\]|\1["e"]|' "$CONFIG_FILE"
  echo "Applied Codespaces override in $CONFIG_FILE (execute_code: [\"e\"])"
elif grep -Eq '^[[:space:]]*bindings:[[:space:]]*$' "$CONFIG_FILE"; then
  sed -i -E '/^[[:space:]]*bindings:[[:space:]]*$/a\  execute_code: ["e"]' "$CONFIG_FILE"
  echo "Added Codespaces execute binding in $CONFIG_FILE (execute_code: [\"e\"])"
else
  cat >> "$CONFIG_FILE" <<'EOF'

bindings:
  execute_code: ["e"]
EOF
  echo "Added bindings block in $CONFIG_FILE with execute_code: [\"e\"]"
fi
