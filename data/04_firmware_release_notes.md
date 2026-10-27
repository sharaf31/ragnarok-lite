# Skylark Firmware — Release Notes

## Firmware 2.4.0 — released 8 September 2026
Applies to: Skylark Pro, Skylark Pro+

### New
- **Lightning proximity alerts** (Pro+ only): uses the existing RF front-end to estimate strikes within 40 km.
- **Frost warning**: push notification when the forecast dew point and temperature indicate ground frost within 6 hours. Requires Skylark Cloud.
- Hub display now supports a dark mode that switches automatically at sunset.

### Changed
- Wind update interval reduced from 16 seconds to **8 seconds**.
- Outdoor array battery life estimate revised to **approximately 14 months** because of the faster wind interval. Users can restore the 16-second interval in Settings → Power → Eco mode, which brings battery life back to about 18 months.
- Maximum offline data buffer on the hub increased from 7 days to 30 days.

### Fixed
- Rain totals no longer reset at midnight UTC instead of local midnight.
- Fixed a crash when the hub language was set to Portuguese and a frost alert arrived.

### Known issues
- On hardware revision A (sold 2021 only), lightning alerts may show false positives near fluorescent lighting. Disable the feature on revision A.

---

## Firmware 2.3.1 — released 14 May 2026
### Fixed
- Wi-Fi reconnect loop on some routers using WPA3 transition mode.
- UV index reported as 0 between 10:00 and 10:01 every day.

---

## Firmware 2.3.0 — released 2 March 2026
### New
- Public API v2 support (see the Skylark Cloud API guide).
- Barometric trend arrow on the hub display.

### Changed
- Minimum supported mobile app version is now 5.0.
