# Process Flow Diagrams — Quà sinh nhật

**Doc**: BA-DEL-05
**Author**: Trang (BA Lead)
**Date**: 2026-05-04
**Version**: 1.0
**Audience**: Toàn team (Devs, QA, Designer, PO, PM)

**Format**: Mermaid diagrams (render trên GitHub, GitLab, Confluence Mermaid plugin, hoặc paste vào https://mermaid.live)

---

## Diagram 1 — End-to-end happy path (KH tier Bạc)

```mermaid
sequenceDiagram
    autonumber
    participant DWH as DWH (MB Ageas)
    participant CC as Customer Care Service
    participant L as Loyalty Service
    participant N as Notification Service
    participant KH as KH (MB Life App)
    participant U as Urbox

    Note over DWH,CC: T-1 (1 ngày trước sinh nhật)
    DWH->>CC: Daily batch sync 02:00
    CC->>CC: Validate + insert/update customer
    CC->>CC: Snapshot tier T-1 02:30<br/>(BR-02)

    Note over CC,KH: Ngày T (sinh nhật)
    CC->>L: birthday_triggered event 09:00<br/>(Kafka)
    L->>L: Pop voucher từ pool<br/>(BR-10 FIFO by expiry)
    L->>CC: pii_transfer_log entry<br/>(audit Đ.16 NĐ 13)
    L->>N: gift_assigned event<br/>(deeplink Urbox)

    par Multi-channel send
        N->>KH: Push notification 09:00
        N->>KH: Email
        N->>KH: Zalo OA message
    end

    KH->>KH: Mở app
    KH->>N: Popup hiển thị (animation confetti)
    KH->>L: Click "Nhận quà"<br/>(màn Quà của tôi)
    L->>U: Activate voucher API
    U-->>L: activated_at + redeem URL
    L->>KH: Redirect deeplink Urbox
    KH->>U: Redeem evoucher tại merchant

    Note over U,L: Async webhook
    U->>L: Webhook redeemed
    L->>L: Update voucher_pool.redeemed_at
```

---

## Diagram 2 — Tier classification logic

```mermaid
flowchart TD
    A[Customer record from DWH] --> B{is_deceased?}
    B -- TRUE --> Z[Exclude<br/>BR-04]
    B -- FALSE --> C{customer_id IN<br/>mb_vip_whitelist?}
    C -- YES --> D[tier = MB_VIP]
    C -- NO --> E{APE < 50tr?}
    E -- YES --> F[tier = TIEU_CHUAN]
    E -- NO --> G{APE < 100tr?}
    G -- YES --> H[tier = BAC]
    G -- NO --> I{APE < 300tr?}
    I -- YES --> J[tier = VANG]
    I -- NO --> K[tier = KIM_CUONG<br/>no upper bound]

    D --> L[Snapshot T-1<br/>BR-02]
    F --> L
    H --> L
    J --> L
    K --> L
    L --> M[Lock value<br/>không đổi ngày T]
```

---

## Diagram 3 — Voucher assignment (with fallback)

```mermaid
flowchart TD
    Start[birthday_triggered event] --> Check1{tier eligible?<br/>BAC/VANG/KC/MB_VIP}
    Check1 -- NO --> Skip1[gift_skipped<br/>reason: tier_not_eligible<br/>BR-13 không apply]
    Check1 -- YES --> Check2{gift_opt_out?<br/>BR-13}
    Check2 -- YES --> Skip2[gift_skipped<br/>reason: opt_out]
    Check2 -- NO --> Check3{is_deceased?<br/>BR-04}
    Check3 -- YES --> Skip3[gift_skipped<br/>reason: deceased]
    Check3 -- NO --> Check4{idempotency check<br/>customer_id + event_year + event_type<br/>BR-09}
    Check4 -- already exists --> Skip4[Log: already assigned<br/>NOOP]
    Check4 -- new --> Pop[Pop voucher from pool<br/>BR-10 FIFO by expiry<br/>SELECT FOR UPDATE]
    Pop --> Check5{pool empty?}
    Check5 -- YES --> Pending[Insert gift_assignment<br/>status=PENDING<br/>reason=pool_empty]
    Pending --> Alert[Alert OP +<br/>Send 'Quà đang chuẩn bị' message<br/>BR-11]
    Pending --> Retry24h[Schedule retry +24h]
    Check5 -- NO --> Assign[Insert gift_assignment<br/>status=ASSIGNED<br/>+ update voucher status=ASSIGNED]
    Assign --> Audit[pii_transfer_log entry]
    Audit --> Publish[Publish gift_assigned event<br/>→ Notification Service]
```

---

## Diagram 4 — KH chết post-trigger rollback

```mermaid
sequenceDiagram
    participant DWH
    participant CC as Customer Care
    participant L as Loyalty
    participant N as Notification

    Note over CC: Ngày T 09:00 - KH alive
    CC->>L: birthday_triggered
    L->>L: Assign voucher VC123<br/>status=ASSIGNED
    L->>N: gift_assigned event
    N->>N: Send push/email/zalo

    Note over DWH: Ngày T 12:00 - KH mất
    DWH->>CC: Next sync với is_deceased=TRUE

    Note over CC: Ngày T+1 02:00 (next batch)
    CC->>CC: Detect customer change is_deceased<br/>FALSE → TRUE
    CC->>L: Publish customer_deceased event
    L->>L: Find active gift_assignment(s)<br/>chưa redeem
    L->>L: Set voucher VC123 status=REVOKED<br/>return to pool? NO (already exposed)<br/>BR-04 exception
    L->>L: Update gift_assignment status=REVOKED<br/>reason=deceased_post_trigger
    L->>N: Stop email chuỗi sau (nếu có)

    Note over CC,L: Người thân không nhận voucher (D7)
```

---

## Diagram 5 — Out-of-stock fallback flow

```mermaid
sequenceDiagram
    participant L as Loyalty
    participant N as Notification
    participant KH as KH
    participant OP as OP team

    L->>L: Pop voucher tier VANG
    L->>L: Pool VANG = 0 (out-of-stock)
    L->>L: Insert gift_assignment<br/>status=PENDING<br/>reason=pool_empty
    L->>OP: PagerDuty alert 'Pool VANG empty'
    L->>N: gift_pending event
    N->>KH: Push 'Quà đang chuẩn bị, kiểm tra lại 24h'

    Note over OP: Within 24h
    OP->>L: Rush procurement với Urbox<br/>Upload batch mới qua Admin Portal
    L->>L: Pool VANG = 50 (refilled)

    Note over L: Scheduled retry +24h
    L->>L: Job retry pending assignments
    L->>L: Pop voucher → success
    L->>L: gift_assignment status=ASSIGNED
    L->>N: gift_assigned event
    N->>KH: Push 'Quà của Quý khách đã sẵn sàng'
```

---

## Diagram 6 — Voucher redemption (KH click Nhận quà)

```mermaid
sequenceDiagram
    participant KH
    participant App as MB Life App
    participant L as Loyalty Service
    participant U as Urbox

    KH->>App: Open màn Quà của tôi
    App->>L: GET /api/gifts/customer/{id}
    L-->>App: gift_assignment list
    App-->>KH: Hiển thị card "Quà sinh nhật 150K - Chưa nhận"

    KH->>App: Tap "Nhận quà"
    App->>L: POST /api/gifts/{assignment_id}/activate
    L->>L: Check status = ASSIGNED<br/>(prevent double activate)
    L->>U: POST /api/voucher/activate<br/>{code: VC123}
    U-->>L: 200 OK<br/>{activated_at, redeem_url}
    L->>L: Update voucher status=ACTIVATED<br/>+ activated_at
    L->>L: pii_transfer_log entry
    L-->>App: Return redeem_url
    App->>KH: Open in-app browser<br/>navigate redeem_url
    KH->>U: Redeem at merchant page

    Note over U,L: Webhook async
    U->>L: POST /webhooks/urbox/redeemed
    L->>L: Verify HMAC signature
    L->>L: Update voucher status=REDEEMED<br/>+ redeemed_at
```

---

## Diagram 7 — KH journey (Tiêu chuẩn — không nhận quà)

```mermaid
flowchart LR
    Start[KH tier=Tiêu chuẩn<br/>Ngày sinh nhật] --> T7{Lần đầu năm 2026?<br/>UC-09 D4}
    T7 -- YES --> Pre[T-7: Email pre-birthday<br/>'Chương trình quà thay đổi']
    T7 -- NO --> Skip[Skip pre-birthday]
    Pre --> T0
    Skip --> T0
    T0[Ngày T 09:00] --> Push[Push noti wording cũ<br/>không CTA]
    T0 --> Email[Email chúc mừng wording cũ]
    T0 --> Zalo[Zalo OA message<br/>OP cung cấp template]
    Push --> Open[KH mở app]
    Open --> Popup[Popup hiển thị<br/>không CTA]
    Open --> MyGifts[Vào màn Quà của tôi]
    MyGifts --> Empty['Cảm ơn Quý khách đã đồng hành.<br/>Hiện chưa có quà sinh nhật năm nay']
```

---

## Diagram 8 — System Context (high-level)

```mermaid
flowchart TB
    subgraph External
        DWH[DWH<br/>MB Ageas Group]
        Urbox[Urbox<br/>Voucher partner]
        MBBank[MB Bank<br/>MB-VIP whitelist]
        FCM[Firebase / APNs]
        SMTP[SMTP Gateway]
        Zalo[Zalo OA API]
    end

    subgraph MBL Customer Platform
        CC[Customer Care Service<br/>NEW]
        L[Loyalty Service<br/>NEW]
        N[Notification Service]
        UI[Admin Portal]
        APP[MB Life Style App]
        CRM[CRM Portal<br/>CSKH]
    end

    DWH -->|Daily batch 02:00| CC
    MBBank -->|Quarterly file| UI
    UI -->|Upload| CC
    UI -->|Upload pool| L

    CC -->|Kafka events| L
    L -->|Kafka events| N

    L <-->|REST + webhook| Urbox
    N --> FCM
    N --> SMTP
    N --> Zalo

    APP <-->|REST| CC
    APP <-->|REST| L
    CRM <-->|REST admin API| CC
    CRM <-->|REST admin API| L
```

---

## Diagram 9 — Data lineage

```mermaid
flowchart LR
    subgraph DWH
        D1[customer_master]
        D2[policy_master]
        D3[deceased_register]
    end

    subgraph CC[(customer_care_database)]
        T1[customer]
        T2[customer_tier_snapshot]
        T3[mb_vip_whitelist]
        T4[pii_transfer_log]
        T5[customer_consent]
    end

    subgraph L[(loyalty_database)]
        V1[voucher_pool]
        V2[gift_assignment]
        V3[voucher_pool_audit]
    end

    D1 -->|customer_id, name, phone, email, DOB| T1
    D2 -->|aggregate APE| T1
    D3 -->|is_deceased flag| T1

    T1 -->|compute tier| T2
    T3 -->|override| T2

    T2 -->|trigger| V2
    V1 -->|pop FIFO| V2
    V2 -->|sensitive transfer| T4
    T5 -->|consent check| T4
```

---

## How to render

- **GitHub/GitLab/Confluence Mermaid plugin**: paste blocks above directly.
- **Online**: https://mermaid.live → paste 1 block → export PNG/SVG.
- **VSCode**: install "Markdown Preview Mermaid Support" extension.

## Notes for Designer (Duy)

Diagram 1 + 6 đặc biệt quan trọng cho UX:
- **Diagram 1 step 13**: Popup hiển thị animation confetti — em note phối hợp với Marketing về confetti asset.
- **Diagram 6 step 8-10**: KH click Nhận quà → tương tác giữa app + Urbox redirect — UX cần loading state mượt + handle case Urbox 5xx.
