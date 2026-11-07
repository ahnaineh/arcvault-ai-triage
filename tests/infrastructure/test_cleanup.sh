#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cat > "$tmp/docker" <<'MOCK'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$LOG"
case "$*" in
  'network create '*) echo "owned-${*: -1}" ;;
  create*) exit 1 ;;
esac
MOCK
chmod +x "$tmp/docker"
for n in 1 2; do
  if LOG="$tmp/$n" PATH="$tmp:$PATH" ARCVAULT_INFRA_OPT_IN=yes bash "$root/tests/infrastructure/run.sh"; then exit 1; fi
  ! grep -q '^rm ' "$tmp/$n"
  grep -q '^network rm owned-arcvault-infra-' "$tmp/$n"
done
[ "$(head -1 "$tmp/1")" != "$(head -1 "$tmp/2")" ]
echo 'PASS: failed startup cleans only its owned network; invocations use distinct names'
