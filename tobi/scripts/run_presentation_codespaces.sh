#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOBI_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$TOBI_DIR/.." && pwd)"

INSTALL_ONLY="false"
THEME="terminal-dark"

for arg in "$@"; do
  case "$arg" in
    --install-only)
      INSTALL_ONLY="true"
      ;;
    terminal-dark|terminal-light)
      THEME="$arg"
      ;;
  esac
done

if ! command -v pixi >/dev/null 2>&1; then
  echo "Pixi not found. Installing..."
  curl -fsSL https://pixi.sh/install.sh | bash
fi

export PATH="$HOME/.pixi/bin:$PATH"

if [[ -f "$HOME/.bashrc" ]] && ! grep -Fq 'export PATH="$HOME/.pixi/bin:$PATH"' "$HOME/.bashrc"; then
  echo 'export PATH="$HOME/.pixi/bin:$PATH"' >> "$HOME/.bashrc"
fi

if [[ "$INSTALL_ONLY" == "true" ]]; then
  echo "Pixi bootstrap complete (install-only mode)."
  exit 0
fi

if [[ "${CODESPACES:-}" == "true" ]]; then
  bash "$SCRIPT_DIR/config_codespaces.sh"
fi

cd "$REPO_ROOT"
pixi run presentation_codespaces "$THEME"