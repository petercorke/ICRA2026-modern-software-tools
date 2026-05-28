#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${CODESPACES:-}" != "true" ]]; then
	exit 0
fi

PRESENTERM_CONFIG="$SCRIPT_DIR/../presenterm_config.yaml"
if [[ -f "$PRESENTERM_CONFIG" ]]; then
	if grep -Eq '^[[:space:]]*execute_code:[[:space:]]*\[.*\][[:space:]]*$' "$PRESENTERM_CONFIG"; then
		sed -E -i 's|^([[:space:]]*execute_code:[[:space:]]*)\[.*\][[:space:]]*$|\1["e"]|' "$PRESENTERM_CONFIG"
	elif grep -Eq '^[[:space:]]*bindings:[[:space:]]*$' "$PRESENTERM_CONFIG"; then
		sed -i '/^[[:space:]]*bindings:[[:space:]]*$/a\  execute_code: ["e"]' "$PRESENTERM_CONFIG"
	else
		printf '\nbindings:\n  execute_code: ["e"]\n' >> "$PRESENTERM_CONFIG"
	fi
fi

if [[ -f "$HOME/.bashrc" ]]; then
	for line in \
		'export DISPLAY=:99' \
		'export QT_QPA_PLATFORM=xcb'; do
		if ! grep -Fqx "$line" "$HOME/.bashrc"; then
			printf '%s\n' "$line" >> "$HOME/.bashrc"
		fi
	done
fi

if command -v sudo >/dev/null 2>&1; then
	SUDO=sudo
else
	SUDO=
fi

if ! command -v Xvfb >/dev/null 2>&1 || \
	 ! command -v x11vnc >/dev/null 2>&1 || \
	 ! command -v websockify >/dev/null 2>&1 || \
	 ! command -v fluxbox >/dev/null 2>&1; then
	${SUDO} apt-get update
	${SUDO} apt-get install -y xvfb x11vnc websockify novnc fluxbox libxcb-cursor0
fi

RUNTIME_DIR="$HOME/.cache/icra2026_codespaces"
mkdir -p "$RUNTIME_DIR"

if [[ ! -f "$RUNTIME_DIR/xvfb.pid" ]] || ! kill -0 "$(cat "$RUNTIME_DIR/xvfb.pid")" 2>/dev/null; then
	nohup Xvfb :99 -screen 0 1600x900x24 -nolisten tcp >"$RUNTIME_DIR/xvfb.log" 2>&1 &
	echo $! > "$RUNTIME_DIR/xvfb.pid"
fi

for _ in $(seq 1 50); do
	[[ -S /tmp/.X11-unix/X99 ]] && break
done

if [[ ! -f "$RUNTIME_DIR/fluxbox.pid" ]] || ! kill -0 "$(cat "$RUNTIME_DIR/fluxbox.pid")" 2>/dev/null; then
	nohup env DISPLAY=:99 fluxbox >"$RUNTIME_DIR/fluxbox.log" 2>&1 &
	echo $! > "$RUNTIME_DIR/fluxbox.pid"
fi

if [[ ! -f "$RUNTIME_DIR/x11vnc.pid" ]] || ! kill -0 "$(cat "$RUNTIME_DIR/x11vnc.pid")" 2>/dev/null; then
	nohup x11vnc -display :99 -rfbport 5901 -forever -shared -nopw >"$RUNTIME_DIR/x11vnc.log" 2>&1 &
	echo $! > "$RUNTIME_DIR/x11vnc.pid"
fi

if [[ ! -f "$RUNTIME_DIR/websockify.pid" ]] || ! kill -0 "$(cat "$RUNTIME_DIR/websockify.pid")" 2>/dev/null; then
	nohup websockify --web=/usr/share/novnc 6080 localhost:5901 >"$RUNTIME_DIR/websockify.log" 2>&1 &
	echo $! > "$RUNTIME_DIR/websockify.pid"
fi

echo "Codespaces desktop is available on DISPLAY=:99 and browser port 6080."
