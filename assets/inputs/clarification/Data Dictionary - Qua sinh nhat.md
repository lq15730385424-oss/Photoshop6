# Data Dictionary — Quà sinh nhật

**Doc**: BA-DEL-04
**Author**: Trang (BA Lead)
**Date**: 2026-05-04
**Version**: 1.0
**Audience**: Devs (Cường + team), Data team, DPO

**Mục đích**: Định nghĩa chính xác mọi field, type, constraint, source-of-truth cho luồng Quà sinh nhật. Dev tham chiếu khi implement, Data team khi build ETL.

**DB targets**:
- `customer_care_database` — own bởi Customer Care Service
- `loyalty_database` — own bởi Loyalty Service

---

## Bảng `customer` (customer_care_database)

Source: DWH daily sync (UC-01).

| Field | Type | Nullable | PK/Index | Source | Description |
|---|---|---|---|---|---|
| `customer_id` | VARCHAR(20) | NO | PK | DWH (CIF MBL) | Mã KH duy nhất MBL |
| `cif_mb_bank` | VARCHAR(20) | YES | IDX | DWH | CIF tại MB Bank, dùng cho lookup MB-VIP |
| `full_name` | VARCHAR(255) | NO |  | DWH | Họ tên đầy đủ KH |
| `date_of_birth` | DATE | NO | IDX | DWH | DOB. Constraint: ≤ today |
| `gender` | ENUM('M','F','OTHER') | YES |  | DWH | |
| `phone` | VARCHAR(15) | YES | IDX | DWH | SĐT, format E.164 |
| `email` | VARCHAR(255) | YES |  | DWH | Email, validated format |
| `total_active_ape` | DECIMAL(15,0) | NO |  | DWH | Tổng APE các HĐBH active. Đơn vị VND. ≥0 |
| `is_deceased` | BOOLEAN | NO |  | DWH | TRUE = KH đã mất, exclude khỏi events |
| `gift_opt_out` | BOOLEAN | NO |  | App settings | KH chủ động opt-out nhận quà |
| `gift_consent_active` | BOOLEAN | NO |  | App consent flow | Consent share data với Urbox (NĐ 13) |
| `last_synced_at` | TIMESTAMP | NO |  | System | Last successful DWH sync |
| `created_at` | TIMESTAMP | NO |  | System | |
| `updated_at` | TIMESTAMP | NO |  | System | |

**Constraints**:
- `date_of_birth < CURRENT_DATE`
- `total_active_ape >= 0`
- Index composite: `(date_of_birth, is_deceased)` for snapshot job query

---

## Bảng `customer_tier_snapshot` (customer_care_database)

Source: Snapshot job T-1 (BR-02).

| Field | Type | Nullable | PK/Index | Source | Description |
|---|---|---|---|---|---|
| `snapshot_id` | UUID | NO | PK | System | |
| `customer_id` | VARCHAR(20) | NO | FK→customer | | |
| `event_date` | DATE | NO | IDX | Computed (next birthday) | Ngày event sinh nhật |
| `event_type` | VARCHAR(20) | NO |  | Constant | "BIRTHDAY" / "ANNIVERSARY" |
| `tier` | ENUM | NO |  | Computed | TIEU_CHUAN / BAC / VANG / KIM_CUONG / MB_VIP |
| `total_ape_at_snapshot` | DECIMAL(15,0) | NO |  | Customer | APE tại moment snapshot |
| `is_mb_vip_at_snapshot` | BOOLEAN | NO |  | Whitelist | |
| `snapshot_at` | TIMESTAMP | NO |  | System | Job run time |

**Unique constraint**: `(customer_id, event_date, event_type)` — đảm bảo BR-09 idempotency.

---

## Bảng `mb_vip_whitelist` (customer_care_database)

Source: MB Bank file Excel quarterly (D3).

| Field | Type | Nullable | PK/Index | Source | Description |
|---|---|---|---|---|---|
| `whitelist_id` | UUID | NO | PK | System | |
| `customer_id` | VARCHAR(20) | NO | UK | Lookup từ CIF | NULL nếu chưa lookup được |
| `cif_mb_bank` | VARCHAR(20) | NO | IDX | MB Bank file | Source key |
| `effective_from` | DATE | NO |  | File | Khi bắt đầu effective |
| `effective_to` | DATE | YES |  | File / system | NULL = đang active. Set = today nếu remove |
| `source_ref` | VARCHAR(50) | NO |  | File metadata | MB Bank batch reference |
| `imported_at` | TIMESTAMP | NO |  | System | |
| `imported_by` | VARCHAR(50) | NO |  | System | OP user |
| `unmatched_status` | ENUM | YES |  | System | NULL / PENDING / RESOLVED / FAILED. NULL = matched |

**Unique constraint**: `(customer_id, effective_from)` khi customer_id != NULL.

---

## Bảng `voucher_pool` (loyalty_database)

Source: OP upload file Excel từ Urbox (UC-07).

| Field | Type | Nullable | PK/Index | Source | Description |
|---|---|---|---|---|---|
| `voucher_code` | VARCHAR(50) | NO | PK | Urbox file | Mã voucher unique |
| `redeem_url` | VARCHAR(500) | NO |  | Urbox file | Deeplink redeem |
| `face_value` | DECIMAL(10,0) | NO |  | Urbox file | Mệnh giá (VND). Enum {150K,200K,500K,1M,2M} |
| `tier_eligibility` | ENUM | NO | IDX | Computed from face_value | BAC/VANG/KIM_CUONG/MB_VIP |
| `batch_id` | UUID | NO | IDX | OP upload | Batch reference |
| `imported_at` | TIMESTAMP | NO |  | System | |
| `imported_by` | VARCHAR(50) | NO |  | System | OP user |
| `expires_at` | TIMESTAMP | NO | IDX | Urbox file | Hạn voucher |
| `status` | ENUM | NO | IDX | System | AVAILABLE/ASSIGNED/REDEEMED/EXPIRED/REVOKED |
| `assigned_to_customer_id` | VARCHAR(20) | YES | IDX | Loyalty Service | NULL nếu AVAILABLE |
| `assigned_at` | TIMESTAMP | YES |  | System | |
| `activated_at` | TIMESTAMP | YES |  | Urbox webhook | Khi KH click Nhận quà (BR-12) |
| `redeemed_at` | TIMESTAMP | YES |  | Urbox webhook | Khi KH redeem voucher tại merchant |

**Index composite**:
- `(tier_eligibility, status, expires_at ASC)` — fast pop FIFO theo expiry
- `(assigned_to_customer_id)` for customer lookup

---

## Bảng `gift_assignment` (loyalty_database)

Source: Loyalty Service tại moment trigger event.

| Field | Type | Nullable | PK/Index | Source | Description |
|---|---|---|---|---|---|
| `assignment_id` | UUID | NO | PK | System | |
| `customer_id` | VARCHAR(20) | NO | IDX | | |
| `event_date` | DATE | NO |  | Snapshot | |
| `event_type` | VARCHAR(20) | NO |  | Snapshot | "BIRTHDAY" / "ANNIVERSARY" |
| `event_year` | INT | NO |  | event_date | Computed cho idempotency |
| `tier_at_assignment` | ENUM | NO |  | Snapshot | |
| `voucher_code` | VARCHAR(50) | YES | FK→voucher_pool | Pool pop | NULL nếu pending hoặc skipped |
| `status` | ENUM | NO | IDX | System | ASSIGNED/PENDING/SKIPPED/REVOKED |
| `pending_reason` | VARCHAR(50) | YES |  | System | "pool_empty" / "tier_not_eligible" / "opt_out" / "deceased" |
| `assigned_at` | TIMESTAMP | NO |  | System | |
| `last_retry_at` | TIMESTAMP | YES |  | System | Cho status PENDING |
| `retry_count` | INT | NO | DEFAULT 0 | | |

**Unique constraint**: `(customer_id, event_year, event_type)` — BR-09 idempotency.

---

## Bảng `pii_transfer_log` (customer_care_database)

Source: Mọi lần đẩy PII sang external system (Urbox, GHN, ...). Section 7 BRD.

| Field | Type | Nullable | PK/Index | Source | Description |
|---|---|---|---|---|---|
| `log_id` | UUID | NO | PK | System | |
| `customer_id` | VARCHAR(20) | NO | IDX | | |
| `recipient_system` | VARCHAR(50) | NO | IDX | System | "URBOX" / "GHN" / "ZALO_OA" |
| `fields_transferred` | JSONB | NO |  | System | Array of field names ["customer_id","face_value"] |
| `legal_basis` | ENUM | NO |  | System | CONSENT/CONTRACT/LEGITIMATE_INTEREST |
| `consent_id` | UUID | YES | FK→consent_record | NULL nếu không phải CONSENT |
| `purpose` | VARCHAR(100) | NO |  | System | "BIRTHDAY_GIFT_ASSIGNMENT" |
| `request_id` | VARCHAR(50) | NO | IDX | System | Correlation ID end-to-end |
| `transferred_at` | TIMESTAMP | NO | IDX | System | |
| `retention_until` | TIMESTAMP | NO |  | System | transferred_at + 5 năm |
| `ip_address` | INET | NO |  | System | IP của caller |
| `status` | ENUM | NO |  | System | SUCCESS / FAILED |
| `error_detail` | TEXT | YES |  | System | Nếu FAILED |

**Retention**: 5 năm theo standard insurance audit. Auto-purge job hàng tháng.

---

## Bảng `customer_consent` (customer_care_database)

Source: App consent flow + DPO admin actions.

| Field | Type | Nullable | PK/Index | Description |
|---|---|---|---|---|
| `consent_id` | UUID | NO | PK | |
| `customer_id` | VARCHAR(20) | NO | IDX | |
| `purpose` | VARCHAR(100) | NO |  | "BIRTHDAY_GIFT" / "MARKETING" / ... |
| `legal_basis` | ENUM | NO |  | CONSENT/CONTRACT/LEGITIMATE_INTEREST |
| `granted` | BOOLEAN | NO |  | TRUE = opt-in, FALSE = withdrawn |
| `granted_at` | TIMESTAMP | NO |  | |
| `withdrawn_at` | TIMESTAMP | YES |  | |
| `version` | VARCHAR(20) | NO |  | T&C version KH đã đồng ý |
| `granted_via` | VARCHAR(50) | NO |  | "APP_SETTINGS" / "ONBOARDING" / "DPO_ADMIN" |

---

## Bảng `voucher_pool_audit` (loyalty_database)

Source: Mọi thao tác trên pool (upload, rollback, manual adjustment).

| Field | Type | Description |
|---|---|---|
| `audit_id` | UUID PK | |
| `action` | ENUM | UPLOAD/ROLLBACK/REVOKE/MANUAL_ADJUST |
| `batch_id` | UUID | |
| `user_id` | VARCHAR(50) | OP/Admin |
| `details` | JSONB | row count, mệnh giá breakdown |
| `file_hash` | VARCHAR(64) | SHA-256 của file uploaded |
| `created_at` | TIMESTAMP | |

---

## Enum definitions

### `customer_tier`
| Value | Display | Threshold |
|---|---|---|
| `TIEU_CHUAN` | Tiêu chuẩn | APE < 50tr & not in MB-VIP |
| `BAC` | Bạc | 50tr ≤ APE < 100tr |
| `VANG` | Vàng | 100tr ≤ APE < 300tr |
| `KIM_CUONG` | Kim cương | APE ≥ 300tr |
| `MB_VIP` | MB-VIP | In whitelist (override APE) |

### `voucher_status`
| Value | Description |
|---|---|
| `AVAILABLE` | Trong pool, sẵn sàng assign |
| `ASSIGNED` | Đã gán cho KH, chưa activate |
| `ACTIVATED` | KH đã click Nhận quà, Urbox start clock |
| `REDEEMED` | KH đã redeem tại merchant |
| `EXPIRED` | Quá hạn |
| `REVOKED` | Bị recall (do KH chết, sai customer, ...) |

### `assignment_status`
| Value | Description |
|---|---|
| `ASSIGNED` | Voucher đã gán |
| `PENDING` | Chưa gán (out-of-stock hoặc đang xử lý) |
| `SKIPPED` | Cố tình không gán (opt-out, deceased, tier không đủ) |
| `REVOKED` | Đã gán nhưng recall sau (KH chết post-trigger) |

### `recipient_system`
| Value | Used in |
|---|---|
| `URBOX` | Voucher partner |
| `GHN` / `GHTK` / `JT` / `VNPOST` | Carrier (giai đoạn 2) |
| `ZALO_OA` | Zalo official account |
| `FCM` / `APNS` | Push notification gateway |
| `SMTP` | Email gateway |

---

## Data flow diagram (text representation)

```
DWH (MB Ageas Group)
    ↓ daily 02:00 batch (Avro/Parquet)
Customer Care Service
    ├── customer table (sync + tier compute)
    ├── customer_tier_snapshot (T-1 02:30)
    └── pii_transfer_log (audit)
        ↓ event birthday_triggered (Kafka, 09:00 ngày T)
Loyalty Service
    ├── voucher_pool (pop FIFO)
    ├── gift_assignment (insert)
    └── pii_transfer_log (audit, customer_id → Urbox)
        ↓ event gift_assigned (Kafka)
Notification Service
    ├── push_notification (FCM/APNs)
    ├── email (SMTP)
    └── zalo (Zalo OA API)
        ↓
KH MB Life Style App
    ├── click "Nhận quà"
    └── deeplink → Urbox redeem page (activate)
        ↓ webhook
Loyalty Service
    └── update voucher_pool.activated_at
```

---

## PII classification (Section 7 BRD)

| Field | NĐ 13 category | Sensitivity | Allowed external? |
|---|---|---|---|
| customer_id | Personal data basic | Low | Urbox: YES, Carrier: YES |
| full_name | Personal data basic | Medium | Urbox: only if needed for personalization, Carrier: YES |
| phone | Personal data basic | Medium | Urbox giai đoạn 1: NO. Carrier giai đoạn 2: YES |
| email | Personal data basic | Medium | NO (MBL gửi email tự) |
| date_of_birth | Personal data basic | Medium | NO |
| gender | Personal data basic | Low | NO |
| total_active_ape | **Financial sensitive (Đ.3.4)** | **High** | **NEVER** |
| cif_mb_bank | Financial identifier | High | NO |
| is_deceased | Inferred sensitive | High | **NEVER** |
| address (giai đoạn 2) | Personal data basic | Medium | Carrier: YES, Urbox: YES (forward to carrier) |

---

## Open data items

| # | Item | Status |
|---|---|---|
| D-O-1 | DWH có sẵn `is_deceased` field hay phải coordinate Group team? | Pending action A3 |
| D-O-2 | DWH có sẵn `cif_mb_bank` field cho lookup MB-VIP? | Pending B6 |
| D-O-3 | Format file Urbox export (Excel, CSV, JSON)? | Pending Hương deal Urbox |
| D-O-4 | Retention `pii_transfer_log` 5 năm có conflict với GDPR-style erasure? | Pending DPO |
