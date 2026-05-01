# Business Rules — Quà sinh nhật

**Doc**: BA-DEL-02
**Author**: Trang (BA Lead)
**Date**: 2026-05-04
**Version**: 1.0
**Status**: Sign-off bởi PO (Thuỳ Giang) ngày 2026-04-30 cho BR-01 → BR-09. BR-10 → BR-15 chờ confirm.

**Mục đích**: Master document tất cả business rules của luồng Quà sinh nhật giai đoạn 1. Dev/QA/Compliance reference văn bản này thay vì đào trong BRD.

---

## BR-01: Phân hạng KH theo APE + MB-VIP whitelist

**Source**: PO decision 2026-04-30 + BU Excel R10-R15 + PM directive

**Rule**: Mỗi KH được gán 1 trong 5 hạng theo logic priority sau:

```
IF customer_id IN mb_vip_whitelist:
    tier = "MB_VIP"
ELIF total_active_APE < 50_000_000:
    tier = "TIEU_CHUAN"
ELIF total_active_APE < 100_000_000:
    tier = "BAC"
ELIF total_active_APE < 300_000_000:
    tier = "VANG"
ELSE:
    tier = "KIM_CUONG"      # ≥300tr, không có ngưỡng trên
```

**Value evoucher theo tier**:
| Tier | Value |
|---|---:|
| TIEU_CHUAN | 0đ (chỉ chúc mừng) |
| BAC | 150.000đ |
| VANG | 200.000đ |
| KIM_CUONG | 500.000đ |
| MB_VIP | TBD (Marketing chốt — 1tr-2tr) |

**Exception**: MB-VIP whitelist override mọi APE rule. KH MB-VIP có APE 0đ vẫn là MB-VIP.

---

## BR-02: Snapshot tier tại T-1

**Source**: PO decision 2026-04-30

**Rule**: Tier áp dụng cho event sinh nhật là tier compute tại snapshot **T-1 ngày sinh nhật**. Lưu vào `customer_tier_snapshot` với key (`customer_id`, `event_date`). Snapshot không thay đổi trong ngày T.

**Validation logic**:
```
event_date = customer.next_birthday()
snapshot_at = event_date - 1 day, time 02:30
tier_locked = compute_tier(customer.APE_at(snapshot_at))
```

---

## BR-03: KH sinh ngày 29/2

**Source**: PO decision 2026-04-30

**Rule**: KH có DOB = 29/2:
- Năm nhuận: tổ chức sinh nhật ngày 29/2.
- Năm thường: tổ chức sinh nhật ngày **28/2**.

**Examples**:
- KH DOB = 2000-02-29
- 2024 nhuận → event_date = 2024-02-29
- 2025 thường → event_date = 2025-02-28
- 2026 thường → event_date = 2026-02-28

---

## BR-04: Loại trừ KH đã mất

**Source**: PO decision + DPO

**Rule**: KH có `is_deceased = TRUE`:
- **Không trigger** push noti, popup, email, zalo.
- **Không assign voucher**.
- Lưu trong DB cho audit trail (không xoá record).

**Exception**: KH chuyển sang `is_deceased = TRUE` **sau** khi đã trigger gửi quà nhưng **chưa redeem**:
- Rollback voucher (return code về pool, status REVOKED).
- Stop email chuỗi sau (nếu có).
- Mark customer event = "skipped_deceased".
- Alert OP để follow-up người thân nếu cần (không transfer voucher cho người thân — D7).

---

## BR-05: Tần suất sync DWH → Customer Care

**Source**: SA (Vũ) decision

**Rule**: DWH push customer batch daily 02:00. Customer Care Service consume + validate + insert/update bảng `customer`. Snapshot tier job chạy 02:30 sau khi sync hoàn tất.

**Late data handling**: Nếu DWH push trễ (sau 03:00), trigger sinh nhật vẫn dùng snapshot từ batch cũ (đã có T-1). Job snapshot không retry — accept stale data tối đa 1 ngày.

---

## BR-06: Anti-duplicate Customer ID

**Source**: BRD UC-01 v0.1

**Rule**: `customer_id` là key duy nhất. Nếu DWH push nhiều bản ghi cùng customer_id:
- Gộp thành 1 record.
- Thông tin (name, DOB, phone, email): lấy theo bản ghi cập nhật mới nhất.
- APE: tính tổng của tất cả bản ghi cùng customer_id.
- KHÔNG check trùng theo SĐT/Email.

---

## BR-07: Update existing — không ghi đè null

**Source**: BRD UC-01 v0.1

**Rule**: Khi update customer existing, chỉ update field khi giá trị mới không null.

**Example**:
- DB hiện tại: `email = 'abc@gmail.com'`
- DWH push: `email = NULL`
- → Giữ nguyên `'abc@gmail.com'` (không ghi đè bằng null)

---

## BR-08: Frequency push noti / popup / email

**Source**: BRD UC-03, UC-04, UC-05 + Excel R14

**Rule**:
| Kênh | Thời điểm | Tần suất |
|---|---|---|
| Push noti | 09:00 sáng ngày T | 1 lần/ngày |
| In-app noti | 00:00 ngày T | 1 lần/ngày |
| Popup | Khi KH login app ngày T | 1 lần/ngày (tracking session) |
| Email | 09:00 sáng ngày T | 1 lần |
| Zalo | 09:00 sáng ngày T | 1 lần |
| **SMS** | — | **Không gửi** (Excel R14) |

---

## BR-09: Idempotency event sinh nhật

**Source**: SA (Vũ) decision A2

**Rule**: Event birthday_triggered có idempotency key = `(customer_id, event_year, event_type='BIRTHDAY')`. Nếu replay, Loyalty Service skip không assign voucher lần 2.

**Implementation**: Bảng `gift_assignment` có UNIQUE constraint trên `(customer_id, event_year, event_type)`.

---

## BR-10: Voucher pool — voucher selection logic

**Source**: SA (Vũ) decision A4

**Rule**: Khi assign voucher cho KH tier X:
1. Query `voucher_pool WHERE tier_eligibility = X AND status = 'AVAILABLE'`.
2. ORDER BY `expires_at ASC` (FIFO theo expiry — voucher hết hạn sớm nhất dùng trước).
3. SELECT 1 row, UPDATE status = 'ASSIGNED' với `assigned_to_customer_id` + `assigned_at`.
4. Sử dụng SELECT FOR UPDATE để tránh race condition.

**Out-of-stock**: Nếu không có row AVAILABLE → throw `PoolEmptyException` → BR-11 fallback.

---

## BR-11: Out-of-stock fallback

**Source**: 3-bên meeting D6

**Rule**: Khi pool tier X out-of-stock tại moment trigger sinh nhật:
1. Insert `gift_assignment_pending` record.
2. Push noti / email / popup gửi với content: *"Quà của Quý khách đang được chuẩn bị, vui lòng kiểm tra lại trong 24h"*.
3. OP nhận alert, rush procurement.
4. Job retry sau 24h, 48h, 72h. Sau 72h vẫn fail → escalate manual.
5. **Không** downgrade tier (không tặng Bạc cho KH Vàng).

---

## BR-12: Voucher activation time

**Source**: 3-bên meeting D1

**Rule**: Voucher Urbox có hạn 6 tháng tính từ ngày MBL **activate code** (khi KH click "Nhận quà" lần đầu — không phải từ ngày Urbox xuất batch).

**Implementation**: API call sang Urbox khi KH click → Urbox start clock + return `activated_at`.

---

## BR-13: KH opt-out gift

**Source**: B-21 (Q&A BU) + DPO requirement

**Rule**: KH có `gift_opt_out = TRUE`:
- Vẫn nhận chúc mừng (push noti / popup / email với wording cũ).
- Không assign voucher.
- Mark event "gift_skipped" reason "opt_out".

KH có thể opt-out qua:
- Settings → Privacy trên app (self-service).
- Yêu cầu qua CSKH.

---

## BR-14: KH chỉ tính HĐ cá nhân

**Source**: BRD UC-01

**Rule**: KH được tính sinh nhật và APE chỉ khi có HĐBH **cá nhân** (BMBH cá nhân) với ít nhất 1 hợp đồng status Active. KH chỉ là NĐBH của HĐ doanh nghiệp **không** được tính.

---

## BR-15: KH < 18 tuổi

**Source**: BA derivation từ Luật KDBH

**Rule**: KH có tuổi < 18 (tính từ DOB):
- Theo Luật KDBH 2022, không ai dưới 18 tuổi là BMBH (chỉ là NĐBH).
- Vì BR-14 chỉ tính BMBH cá nhân, KH <18 tự động không có trong dataset.
- **Không cần xử lý đặc biệt** ở Customer Care Service.

**Note**: Edge case có thể xảy ra nếu DWH bug → cần validation reject `IF age < 18: log warn`.

---

## Pending rules (chờ confirm)

| ID | Rule | Owner | Status |
|---|---|---|---|
| BR-PEND-1 | Value evoucher MB-VIP | Marketing | Block UC-01 final |
| BR-PEND-2 | Pre-birthday email UC-09 wording | Marketing | B8 deadline W20 |
| BR-PEND-3 | Quà có refund/cancel khi link sai | OP + Urbox | A5 |
| BR-PEND-4 | Cross-border PII (Urbox AWS region) | DPO | Section 7.5 BRD |

---

## Change log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | 2026-04-25 | Initial draft từ BRD | Trang |
| 0.2 | 2026-04-30 | Update sau PO sign-off + 3-bên meeting | Trang |
| 1.0 | 2026-05-04 | Consolidate + ready for grooming W19 | Trang |
