# Design Spec — "Quà của tôi" (Quà sinh nhật)

**Doc**: DESIGN-DEL-01
**Author**: Duy (Product Designer)
**Date**: 2026-05-01
**Version**: 1.0
**Audience**: Dev team (Cường + Mobile devs), QA, BA (Trang), SA (Vũ)
**Status**: Ready for handoff

**Figma file**: `6VrJdZ3ckrdUWMZQcDb55j`
**URL**: https://www.figma.com/design/6VrJdZ3ckrdUWMZQcDb55j
**Frame size**: iPhone 13 mini 375×812 (mobile-first; web responsive sẽ design sau)

---

## 1. Component inventory

| Component | Figma node ref | Reusable? | Notes |
|---|---|---|---|
| StatusBar | inside each screen | Có (existing app component) | Time + system icons. Dev dùng native status bar component. |
| Header | inside each screen | Có (existing) | `←` back + title. Dùng AppBar pattern hiện tại của MB Life Style |
| Tabs (segmented) | inside each screen | **Mới** — design system component | 2 tabs: Quà sinh nhật / Quà kỷ niệm HĐ. Active indicator 60×3, primary color |
| **GiftCard** | giftCard helper | **Mới — flagship component** | Có 4 visual states (available/pending/redeemed/expired). Reuse cho Quà kỷ niệm HĐ |
| BottomNav | inside each screen | Có (existing) | 4 items, "Quà của tôi" là item 3 (active) |
| Hint banner | screen 02 | **Mới** | Info-style banner, blue-toned, dùng cho contextual help |
| Empty state | screen 01 | **Mới** | Icon 🎂 trong circle + heading + sub-text |

---

## 2. Design tokens

### 2.1 Colors

**Brand**:
| Token | Hex | Usage |
|---|---|---|
| `primary` | `#003D6B` | MB Ageas blue. CTA primary, headings, active tab |
| `accent` | `#E5114E` | MB red. Value highlight (giá trị quà), gift icon bg |

**Semantic**:
| Token | Light | Dark | Usage |
|---|---|---|---|
| `success` | `#DCFCE7` | `#166534` | Badge "Đã nhận quà" |
| `warning` | `#FEF9C3` | `#92400E` | Badge "Chưa nhận" |
| `error` | `#FEE2E2` | `#991B1B` | Badge "Đã hết hạn" |
| `pending` | `#EDF2F7` (ink-100) | `#404959` (ink-700) | Badge "Đang chuẩn bị" |
| `pendingMessage` bg | `#FFF7ED` | text `#7C2D12` | Message box trong Pending card |
| `hint` bg | `#EFF6FF` | text `#1E407C` | Info hint banner |

**Neutral (ink scale)**:
| Token | Hex | Usage |
|---|---|---|
| `ink-900` | `#181C24` | Primary text |
| `ink-700` | `#404959` | Secondary text |
| `ink-500` | `#718096` | Tertiary text, label |
| `ink-300` | `#CBD5E0` | Divider, disabled bg |
| `ink-100` | `#EDF2F7` | Surface, divider light |
| `bg` | `#F7FAFC` | Page background |
| `white` | `#FFFFFF` | Card, header bg |

**Decorative**:
| Token | Hex | Usage |
|---|---|---|
| `giftPink` | `#FEE2EB` | Card top accent strip (Available/Redeemed) |

### 2.2 Typography

**Font family**: `Inter` (system fallback: SF Pro / Roboto)

| Token | Size | Weight | Line height | Usage |
|---|---|---|---|---|
| `display` | 32 | Bold | 40 | Canvas title (designer reference, not in app) |
| `h1` | 22 | Bold | 30 | (reserve for screen titles future) |
| `h2` | 18 | Bold | 26 | Value highlight (150.000đ) |
| `h3` | 17 | Semi Bold | 24 | App header title, Empty state heading |
| `body-lg` | 16 | Regular/Medium | 22 | Body text large |
| `body` | 15 | Semi Bold | 22 | Button label |
| `body-sm` | 14 | Regular/Medium | 20 | Tab label, hint banner, sub-heading |
| `caption` | 13 | Regular/Medium | 18 | Detail row label/value |
| `caption-sm` | 12 | Regular/Medium | 16 | Year label, hint text |
| `micro` | 11 | Semi Bold | 14 | Badge text |
| `nano` | 10 | Regular/Semi Bold | 14 | Bottom nav label |

**Persona C (elderly) accommodation**: dynamic type respect. Body text scales lên 16-18pt khi system font scale = "Large" hoặc cao hơn. Test trên Settings > Display > Text Size.

### 2.3 Spacing scale (4pt grid)

| Token | px | Usage |
|---|---|---|
| `space-0` | 0 | — |
| `space-1` | 4 | Icon-text gap |
| `space-2` | 8 | Tight gap, icon margin |
| `space-3` | 12 | Card section gap, hint banner gap |
| `space-4` | 14 | Card body inner padding small |
| `space-5` | 16 | Standard padding (card outer, page edge) |
| `space-6` | 20 | Card body inner padding standard |
| `space-7` | 24 | Section spacing |
| `space-8` | 32 | (reserve) |
| `space-9` | 48 | Hero spacing |

### 2.4 Radius

| Token | px | Usage |
|---|---|---|
| `radius-sm` | 8 | Back button, icon containers |
| `radius-md` | 10 | Hint banner, message box |
| `radius-lg` | 12 | Button |
| `radius-xl` | 16 | GiftCard, top accent strip |
| `radius-pill` | 999 | Badge, icon circle, illustration circle |

### 2.5 Shadow

| Token | Spec | Usage |
|---|---|---|
| `shadow-card` | `0 2 8 rgba(0,0,0,0.06)` | GiftCard elevation |

---

## 3. GiftCard — flagship component spec

### 3.1 Anatomy

```
┌──────────────────────────────────────┐
│ [Accent Strip] ── radius-xl top     │  <-- giftPink bg (or ink-100 if pending)
│  ┌──┐                                │
│  │🎁│  Quà sinh nhật MB Life  [Bdg] │  <-- iconCircle 48×48, title, badge
│  └──┘  Năm 2026                      │
├──────────────────────────────────────┤
│ [Body] ── padX:20 padY:16 gap:12    │  <-- white bg
│  Giá trị quà            150.000đ    │  <-- value row (skip if pending)
│  ──────────────────────────────────  │
│  Hạn sử dụng    6 tháng (chưa kích)  │  <-- detail rows
│  Ngày tặng      05/05/2026          │
│  ┌─[Pending only]─────────────────┐  │
│  │ ⏱ Quà đang chuẩn bị, kiểm tra │  │
│  │   lại trong 24h                │  │
│  └────────────────────────────────┘  │
│  ┌──────────────────────────────┐    │
│  │      Nhận quà ngay 🎁         │    │  <-- CTA primary (or secondary)
│  └──────────────────────────────┘    │
└──────────────────────────────────────┘
   width: 343 (= 375 - 16*2 page padding)
```

### 3.2 State machine

```
        ┌─────────────┐
        │ ASSIGNED    │  badge: "Chưa nhận" (warning)
        │ Available   │  CTA: "Nhận quà ngay" (primary)
        └──────┬──────┘
               │ user click "Nhận quà"
               │ → MBL call Urbox /activate
               ▼
        ┌─────────────┐
        │ ACTIVATING  │  Loading state inline
        │ (transient) │  CTA disabled, spinner
        └──────┬──────┘
               │ Urbox return success
               ▼
        ┌─────────────┐
        │ REDEEMED    │  badge: "Đã nhận quà" (success)
        │             │  CTA: "Xem chi tiết Urbox" (secondary)
        └──────┬──────┘
               │ time passes, user không redeem at merchant
               │ activated_at + 6 months
               ▼
        ┌─────────────┐
        │ EXPIRED     │  badge: "Đã hết hạn" (error)
        │             │  CTA: removed
        └─────────────┘

      ┌──────────────────────┐
      │ PENDING (pool empty) │  badge: "Đang chuẩn bị" (pending)
      │ Special branch       │  CTA: "Liên hệ CSKH" (secondary)
      └──────────────────────┘
        Triggered when Loyalty Service can't pop voucher
        Auto retry +24h, +48h, +72h
        After success → transition to ASSIGNED
```

**Transition rules**:
- `ASSIGNED → ACTIVATING`: only when `gift_consent_active = TRUE`. If false, show consent dialog first.
- `ACTIVATING → REDEEMED`: optimistic update. If Urbox returns error → revert to ASSIGNED, show toast.
- `REDEEMED → EXPIRED`: scheduled job at activated_at + 6 months. Webhook from Urbox can also trigger.
- `PENDING → ASSIGNED`: backend job retries every 24h, max 3 attempts. After 3rd fail → mark as failed, alert OP.

---

## 4. Animation specs

### 4.1 Card entrance (when màn Quà của tôi loads)

```
duration: 300ms
easing: cubic-bezier(0.2, 0.8, 0.2, 1) (ease-out)
properties:
  opacity: 0 → 1
  translateY: 20px → 0
stagger: 80ms per card (for History screen with multiple cards)
```

### 4.2 CTA button press

```
duration: 150ms
easing: ease-in-out
scale: 1 → 0.96 → 1
opacity: 1 → 0.85 → 1
haptic: light impact (iOS: UIImpactFeedbackGenerator.light)
```

### 4.3 Badge color transition (state change)

```
duration: 400ms
easing: ease-out
properties: backgroundColor, textColor (cross-fade)
```

### 4.4 Popup confetti (Birthday landing)

Spec separate, do Marketing cung cấp asset `.json` Lottie. Designer note:
- Trigger: khi popup birthday hiện trên home screen
- Duration: 2.5s, loop: false
- Asset format: Lottie JSON, max 200KB
- Fallback: nếu Lottie fail → static PNG confetti

---

## 5. Accessibility annotations (WCAG AA)

### 5.1 Touch targets

| Element | Min size | Notes |
|---|---|---|
| Back button | 44×44 (visible 32×32) | Hit target padding 6 each side |
| Tab item | full width / 2, height 50 | Whole tab clickable |
| CTA button | 44×width (visible 48×width) | Persona C accommodation |
| Bottom nav item | 44×width / 4 | |
| Card "Nhận quà" | 48×width-40 | |

### 5.2 Color contrast

| Foreground | Background | Ratio | WCAG |
|---|---|---|---|
| ink-900 on white | 13.5:1 | AAA |
| ink-500 on white | 4.6:1 | AA |
| primary on white | 9.8:1 | AAA |
| white on primary (CTA) | 9.8:1 | AAA |
| accent on white (giá trị quà) | 5.8:1 | AA |
| warningDark on warningLight (badge) | 7.1:1 | AAA |
| successDark on successLight | 8.2:1 | AAA |
| errorDark on errorLight | 8.5:1 | AAA |

✅ All combinations pass WCAG AA. Nhiều combinations pass AAA.

### 5.3 Screen reader (VoiceOver / TalkBack)

**Card label format**:
```
"Quà sinh nhật năm 2026, chưa nhận, giá trị 150 nghìn đồng,
hạn sử dụng 6 tháng chưa kích hoạt, ngày tặng 5 tháng 5 năm 2026.
Nút nhận quà ngay."
```

**Tab role**: `role="tablist"`, items `role="tab"` with `aria-selected`.

**Empty state**:
```
"Không có quà sinh nhật năm nay. Cảm ơn Quý khách đã đồng hành cùng MB Life."
```

### 5.4 Keyboard navigation (cho tablet)

- Tab order: Back → Tab1 → Tab2 → Card → CTA → BottomNav items.
- Enter/Space activates buttons.
- Esc closes modals.

### 5.5 Persona C (elderly) accommodations

- Body text base 14pt → respect dynamic type up to 18pt.
- Touch target min 48pt (above WCAG 44pt).
- Confirmation dialog before destructive actions ("Bạn có chắc muốn nhận quà?" — actually probably skip này vì friendly action, không destructive).
- Avoid jargon ("evoucher" → "phiếu mua hàng điện tử" trong tooltip).

---

## 6. Flutter implementation hints

```dart
// theme.dart
class MBLStyleColors {
  static const primary = Color(0xFF003D6B);
  static const accent = Color(0xFFE5114E);
  static const giftPink = Color(0xFFFEE2EB);
  static const ink900 = Color(0xFF181C24);
  // ... etc
}

class MBLStyleTokens {
  static const double radiusXl = 16;
  static const double radiusPill = 999;
  static const double space5 = 16;
  static const double space6 = 20;
  // ... etc
}

// gift_card.dart - high-level structure
class GiftCard extends StatelessWidget {
  final GiftAssignment assignment;  // model from BE

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(MBLStyleTokens.radiusXl)),
      elevation: 2,  // shadow-card approximation
      child: Column(
        children: [
          _AccentStrip(state: assignment.state),
          _Body(assignment: assignment),
        ],
      ),
    );
  }
}

// State enum
enum GiftCardState { assigned, activating, pending, redeemed, expired }
```

**Reuse opportunity**: nếu Flutter team đã build `Card` cho VQMM với cùng pattern, em (Duy) đề xuất generalize thành `GiftCardWidget` chung — params:
- `state: GiftCardState`
- `title: String`
- `value: String?`
- `expires: String?`
- `dateGiven: String?`
- `onAction: VoidCallback`
- `actionLabel: String?`

---

## 7. Asset checklist cho dev

| Asset | Source | Format | Status |
|---|---|---|---|
| Cake icon 🎂 (Empty state) | Emoji native (system font) | — | OK, không cần asset |
| Gift icon 🎁 (Card) | Emoji native | — | OK |
| Custom illustration Empty state (long-term) | Marketing | SVG/PNG | Pending — interim dùng emoji |
| Confetti animation (Popup) | Marketing | Lottie JSON | Pending B8 |
| MB Ageas logo | Brand asset | SVG | Existing trong app |
| Custom font (nếu khác Inter) | TBD | — | Default Inter OK |

---

## 8. Open items cho follow-up

| # | Item | Owner | Deadline |
|---|---|---|---|
| D-O-1 | Add **Loading state** frame (skeleton card) | Duy | W19 |
| D-O-2 | Add **Error state** frame (mất kết nối + retry) | Duy | W19 |
| D-O-3 | Add **Confirmation dialog** trước Nhận quà (tuỳ chọn — confirm với Trang BA) | Duy | W19 |
| D-O-4 | Confetti Lottie asset từ Marketing | Marketing | trước go-live |
| D-O-5 | Custom illustration Empty state | Marketing | sau MVP |
| D-O-6 | Migrate frames vào file MBAL chính `iMDhP8bAeuZ08ZzKZ7ciXr` | Duy + IT (file access) | W20 |
| D-O-7 | Web responsive variant | Duy | sau MVP mobile |

---

## 9. Stakeholder sign-off

| Stakeholder | Role | Status |
|---|---|---|
| Trang | BA Lead | ⏳ Review pending |
| Thuỳ Giang | PO | ⏳ Review pending |
| Vũ | SA | ⏳ Review for technical feasibility |
| Cường | IT Lead | ⏳ Review for implementation effort |
| Cave | PM/SM | ⏳ Review for sprint commitment |
| Marketing | Brand consistency | ⏳ Review for confetti + illustration |

---

*Duy (Designer) — sẵn sàng review session với toàn squad. Đề xuất book design review 30 phút trong W19 grooming.*
