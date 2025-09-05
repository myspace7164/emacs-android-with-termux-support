#!/usr/bin/env bash
set -euo pipefail

APK=$1
SIGNED=${2:-"${APK%.apk}_signed.apk"}
KEYSTORE=${ANDROID_KEYSTORE_PATH:-"$HOME/.android/ci_keystore.jks"}
ALIAS=${ANDROID_KEYSTORE_ALIAS:?missing alias}
PASS=${ANDROID_KEYSTORE_PASSWORD:?missing password}

# Sign (zipalign intentionally skipped)
apksigner sign \
  --ks "$KEYSTORE" \
  --ks-pass "pass:$PASS" \
  --key-pass "pass:$PASS" \
  --out "$SIGNED" \
  "$APK"

echo "$SIGNED"
