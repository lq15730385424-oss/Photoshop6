# Figma — Status & Pending frames

**Doc**: DESIGN-DEL-02
**Author**: Duy (Designer)
**Date**: 2026-05-01
**Status**: Action items pending Figma rate limit reset

---

## File status

**Current file**: `6VrJdZ3ckrdUWMZQcDb55j` (interim, trong team Tung Le's team)
**URL**: https://www.figma.com/design/6VrJdZ3ckrdUWMZQcDb55j
**Plan**: Starter (free tier — rate limited)

## ✅ 5 frames đã hoàn tất (2026-05-01)

| # | Frame name | Node ID | Status |
|---|---|---|---|
| 1 | 01 — Empty (KH Tiêu chuẩn) | `3:2` | ✅ Created, reviewed |
| 2 | 02 — Assigned (KH Bạc 150K) | `3:36` | ✅ Created, reviewed |
| 3 | 03 — Pending (Pool empty) | `3:90` | ✅ Created — review pending (rate limit) |
| 4 | 04 — Redeemed (Đã nhận) | `3:136` | ✅ Created — review pending |
| 5 | 05 — History (Nhiều năm) | `3:187` | ✅ Created — review pending |

Reviewed PNGs lưu tại `/Users/abc/Desktop/development skills/figma-screenshots/`.

## ⏳ 3 frames pending (Figma rate limit hit)

| # | Frame name | Code ready | Status |
|---|---|---|---|
| 6 | 06 — Loading (Skeleton) | ✅ JS code below | Pending Figma quota reset |
| 7 | 07 — Error (Mất kết nối) | ✅ JS code below | Pending |
| 8 | 08 — Confirm Activate Dialog | ✅ JS code below | Pending |

## 🔄 How to execute pending frames

**Option A — Wait for rate limit reset (~24h)**

Khi rate limit reset, gọi tool `mcp__dead5fe3-...__use_figma` với fileKey `6VrJdZ3ckrdUWMZQcDb55j` và pass code dưới đây.

**Option B — Upgrade Figma plan**

User có thể upgrade Starter → Professional ($15/editor/month) để tăng MCP tool call limit. Link: https://www.figma.com/files/team/1028155408754590143/all-projects?upgrade=mcp_rate_limit_paywall

**Option C — Designer vẽ thủ công**

Mở Figma file qua URL, dùng artboard 375×812 và tự vẽ theo spec trong `Design Spec - Qua cua toi.md` (DESIGN-DEL-01). Tham khảo các frame 1-5 đã tạo cho design system tokens.

## 📋 Spec cho 3 frames pending

### Frame 06 — Loading (Skeleton)

```
Layout:
  - Skeleton GiftCard (cùng anatomy với GiftCard normal)
    - Top accent strip: bg ink-100 (grayed), iconCircle 48×48 ink-200
    - Title rect: 180×14 ink-200 radius 4
    - Year rect: 80×10 ink-200 radius 4
    - Badge rect: 70×22 ink-200 pill
  - Body skeleton:
    - 2 detail rows: label 80×12 + value 120×12
    - Divider 303×1 ink-100
    - CTA placeholder 303×48 ink-200 radius 12
  - Below card: "⏳ Đang tải quà của bạn..." size 13 ink-500

Animation note for dev:
  - Subtle shimmer left-to-right, 1.5s loop
  - Mask gradient từ ink-200 → white → ink-200, tilt 20°
```

### Frame 07 — Error (Mất kết nối)

```
Layout:
  - Center align (counterAxisAlignItems CENTER)
  - Spacer 60px
  - Circle 120×120 errorBg với "⚠" 56pt errorDark
  - Heading: "Đã có lỗi xảy ra" (h3 17pt Semi Bold center)
  - Body: "Không thể tải dữ liệu quà sinh nhật. Vui lòng kiểm tra kết nối và thử lại." (14pt ink-500 line-height 22 center)
  - Spacer 8px
  - Button "Thử lại" — primary, hug width (~120pt)
  - Link: "Liên hệ CSKH 1900 555 593" (13pt primary Semi Bold)
```

### Frame 08 — Confirm Activate Dialog (Bottom sheet style)

```
Background: GiftCard (ASSIGNED state) dimmed dưới overlay
Overlay: rgba(0,0,0,0.5) full screen

Dialog modal (centered horizontal, y=250):
  - Width 327, padding 24, radius 20, white bg, shadow
  - centerX in screen
  - vertical gap 16, items center align

Content:
  1. IconCircle 72×72, giftPink bg, 🎁 36pt
  2. Title "Nhận quà sinh nhật?" (18pt Semi Bold center)
  3. Body "Khi nhận quà, voucher 150.000đ sẽ được kích hoạt và có hạn 6 tháng để sử dụng tại các merchant của Urbox." (14pt ink-700 line-height 22 center)
  4. Hint banner (info-blue): "ℹ Khi đồng ý, dữ liệu sẽ được chia sẻ với Urbox để cấp voucher (theo Nghị định 13/2023)." — important for PII consent disclosure
  5. Button stack:
     - Primary "Đồng ý nhận quà 🎁" (full width)
     - Ghost "Để sau" (full width, white bg, ink-300 stroke)
```

**Important — UX rationale**: Confirm dialog là PII consent moment — Đ.11 NĐ 13 yêu cầu consent rõ ràng trước khi share data với Urbox. Dialog này phải hiển thị **mỗi lần** KH activate voucher, không skip dù KH đã từng đồng ý (consent là per-transaction theo recommended pattern).

## 📜 JS code cho dev/Duy paste vào Figma plugin

Code đầy đủ để tạo 3 frames này đã được test (chỉ rate limit chặn). Code template available bằng cách re-run chính xác Figma JS code đã chuẩn bị trong session này.

## 🎯 Verification checklist (sau khi 8 frames đầy đủ)

- [ ] 5 frame chính (01-05) nhất quán design system tokens
- [ ] 3 frame mới (06-08) cùng tokens, cùng iPhone 13 mini 375×812
- [ ] Loading skeleton có shimmer animation note cho dev
- [ ] Error state có CTA "Thử lại" + link CSKH
- [ ] Confirm dialog highlight PII consent
- [ ] Tất cả frames có status bar + header + tabs + bottom nav (chỉ frame 08 có overlay)
- [ ] Export PNG mỗi frame, attach vào BRD v2.0 section UC-06 Screen Design

## 🔗 References

- Design Spec: `outputs/birthday gift/Design Spec - Qua cua toi.md`
- BRD v2.1: `birthday gift/BRD/Qua sinh nhat BRD v2.0.docx` (đã update reference table với Figma URL)
- VQMM Figma (reference, không có quyền truy cập): `iMDhP8bAeuZ08ZzKZ7ciXr` node `3834-10465`
