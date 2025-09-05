#!/usr/bin/env bash
set -euo pipefail

EMACS_APK=${1:-emacs.apk}
OUT_APK=${2:-emacs_for_termux.apk}
WORKDIR=$(mktemp -d)
cleanup(){ rm -rf "$WORKDIR"; }
trap cleanup EXIT

# Decode
apktool d -f "$EMACS_APK" -o "$WORKDIR/app"
MANIFEST="$WORKDIR/app/AndroidManifest.xml"
STRINGS_DIR="$WORKDIR/app/res/values"

# Ensure values directory
mkdir -p "$STRINGS_DIR"

# Inject sharedUserId + label into manifest (idempotent)
if ! grep -q 'sharedUserId="com.termux"' "$MANIFEST"; then
  # Insert attribute on the <manifest ...> tag
  # Use xmlstarlet if available; otherwise do a conservative sed insertion
  sed -i '0,/<manifest /s//&android:sharedUserId="com.termux" android:sharedUserLabel="@string\/shared_user_label" /' "$MANIFEST"
fi

# Add the string resource (idempotent)
STRINGS_FILE="$STRINGS_DIR/strings.xml"
if [ ! -f "$STRINGS_FILE" ]; then
  cat > "$STRINGS_FILE" <<'XML'
<resources>
    <string name="shared_user_label">Termux user</string>
</resources>
XML
else
  if ! grep -q 'name="shared_user_label"' "$STRINGS_FILE"; then
    # Insert before closing tag
    sed -i 's#</resources>#    <string name="shared_user_label">Termux user</string>\n</resources>#' "$STRINGS_FILE"
  fi
fi

# Build
apktool b "$WORKDIR/app" -o "$OUT_APK"

echo "$OUT_APK"
