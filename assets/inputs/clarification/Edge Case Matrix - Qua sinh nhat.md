# Edge Case Matrix — Quà sinh nhật

**Doc**: BA-DEL-03
**Author**: Trang (BA Lead)
**Date**: 2026-05-04
**Version**: 1.0
**Audience**: QA team, Devs (Cường + team)

**Mục đích**: Liệt kê đầy đủ edge cases để QA build test plan + Devs handle defensive logic. Phân loại theo P0/P1/P2 priority.

**Conventions**:
- **P0**: Must test, không go-live nếu fail.
- **P1**: Important, có thể workaround nếu fail nhưng phải fix trước Sprint+1.
- **P2**: Nice-to-have, defer được.

---

## Phần 1 — Data sync & validation (UC-01)

| # | Scenario | Precondition | Action | Expected | Priority |
|---|---|---|---|---|---|
| E-001 | DWH file rỗng | DWH push file 0 records | Sync job chạy | Job complete SUCCESS, log "empty batch", không throw error | P0 |
| E-002 | DWH file null DOB | Records có DOB null | Sync | Reject record + log error_log, không break các record khác | P0 |
| E-003 | DWH file invalid DOB | DOB = "31/02/1990" hoặc "99/99/9999" | Sync | Reject record, log error rõ định dạng | P0 |
| E-004 | DWH file future DOB | DOB > today (vd 2030-01-01) | Sync | Reject record + alert (suspicious data) | P0 |
| E-005 | Duplicate customer_id trong batch | Cùng batch có 3 row customer_id=CUS001 | Sync | Gộp thành 1 record, name lấy bản mới nhất, APE tổng | P0 |
| E-006 | Customer_id existing — partial update | DB có CUS001, batch có CUS001 với email=null, phone=updated | Sync | Update phone, giữ email cũ (không ghi đè null) | P0 |
| E-007 | Volume cao (>1M records) | DWH push file 1M rows trong 1 batch | Sync | Process trong <2h, không OOM, dùng batch insert + commit theo chunk 10K | P1 |
| E-008 | DWH push trễ (sau 03:00) | DWH gửi file lúc 04:30 | Snapshot job đã chạy 02:30 | Snapshot dùng data cũ T-2, log warn "stale data" | P1 |
| E-009 | DWH push 2 file 1 ngày | Push lần 1 lúc 02:00, lần 2 lúc 04:00 | Sync | Job idempotent — kết quả như push 1 lần với data mới nhất | P1 |
| E-010 | Encoding lỗi tiếng Việt | Họ tên "Nguyễn Văn A" nhưng UTF-8 broken | Sync | Validate encoding, reject hoặc auto-fix nếu phát hiện được | P1 |

---

## Phần 2 — Tier classification (BR-01, BR-02)

| # | Scenario | Precondition | Action | Expected | Priority |
|---|---|---|---|---|---|
| E-101 | KH APE = 49.999.999đ | Just below threshold Bạc | Compute tier | tier = TIEU_CHUAN | P0 |
| E-102 | KH APE = 50.000.000đ | Exact threshold Bạc | Compute tier | tier = BAC | P0 |
| E-103 | KH APE = 99.999.999đ | Just below Vàng | Compute tier | tier = BAC | P0 |
| E-104 | KH APE = 100.000.000đ | Exact threshold Vàng | Compute tier | tier = VANG | P0 |
| E-105 | KH APE = 1.000.000.000.000đ (1 nghìn tỷ) | Edge cao | Compute tier | tier = KIM_CUONG (no upper bound) | P0 |
| E-106 | KH APE = 0đ + có HĐ active | Rider không phí | Compute tier | tier = TIEU_CHUAN | P1 |
| E-107 | KH APE âm | Bug DWH | Compute tier | Reject + alert | P1 |
| E-108 | KH MB-VIP whitelist + APE 30tr | Whitelist override | Compute tier | tier = MB_VIP (override) | P0 |
| E-109 | KH MB-VIP whitelist + APE 500tr (KC level) | Override KC | Compute tier | tier = MB_VIP (override KC) | P0 |
| E-110 | KH đổi APE giữa T-1 và T | T-1 = Bạc, ngày T phát hành HĐ mới → Vàng | Trigger sinh nhật ngày T | Áp tier Bạc (snapshot T-1) | P0 |
| E-111 | KH HĐ lapse trước T-1 | T-2 lapse, T-1 snapshot | Sync + snapshot | APE tính chỉ HĐ active → tier giảm | P0 |
| E-112 | KH HĐ reinstate trước T-1 | T-2 reinstate, APE tăng | Sync + snapshot | APE tính HĐ active mới → tier tăng | P1 |

---

## Phần 3 — Birthday trigger (UC-03, UC-04)

| # | Scenario | Precondition | Action | Expected | Priority |
|---|---|---|---|---|---|
| E-201 | KH sinh 29/2 năm thường | DOB=2000-02-29, năm 2026 | Trigger | Trigger ngày 28/2/2026 | P0 |
| E-202 | KH sinh 29/2 năm nhuận | DOB=2000-02-29, năm 2024 | Trigger | Trigger ngày 29/2/2024 | P0 |
| E-203 | KH sinh 1/1 | DOB=1990-01-01 | Trigger 1/1/2026 | Trigger normal — không vướng năm cũ/mới | P0 |
| E-204 | KH chết trước sinh nhật | is_deceased=TRUE từ DWH push T-2 | Snapshot T-1 | Skip — không tạo snapshot, không trigger ngày T | P0 |
| E-205 | KH chết giữa T-1 và T | Snapshot đã tạo T-1, chết T-1 evening | Trigger T 09:00 | Cần check is_deceased lại tại moment trigger; skip | P0 |
| E-206 | KH chết sau trigger T, chưa redeem | T 09:00 trigger thành công, T 12:00 chết | KH nhận noti nhưng chưa click | Rollback voucher về pool, mark "skipped_deceased", không gửi email tiếp | P0 |
| E-207 | KH chết sau redeem | Đã redeem evoucher | Chết | Không rollback (Urbox đã issue), MBL không recall | P1 |
| E-208 | Job 09:00 fail | Server crash, scheduler miss | Trigger | Job reschedule sau 5 phút, max retry 3 lần | P0 |
| E-209 | KH login vào 8:55 (5 phút trước trigger) | Mở app | Popup không hiển thị | Vì trigger 9:00 → đến 9:00 mới generate. KH next login sau 9:00 sẽ thấy | P1 |
| E-210 | KH ở timezone khác VN (Mỹ -12h) | KH ở US, sinh nhật ngày 5/5 | Trigger 5/5 09:00 GMT+7 | KH ở US lúc đó là 4/5 19:00. KH nhận noti — accept (không phân tách timezone) | P1 |
| E-211 | KH có 2 HĐBH cùng phát hành ngày sinh nhật | DOB=5/5, HĐ 1 = 5/5/2020, HĐ 2 = 5/5/2021 | Trigger | Vẫn 1 noti / 1 quà (không double trigger) | P0 |
| E-212 | KH duplicate trong DWH (bug) | 2 customer_id khác nhau cùng DOB cùng tên cùng phone | Sync + trigger | 2 KH riêng, 2 voucher (vì system trust customer_id là PK) | P1 |

---

## Phần 4 — Voucher pool (UC-07)

| # | Scenario | Precondition | Action | Expected | Priority |
|---|---|---|---|---|---|
| E-301 | Pool tier Vàng = 0 | Out-of-stock | Trigger KH Vàng | Insert pending, gửi message "đang chuẩn bị", retry 24h | P0 |
| E-302 | Pool tier Vàng = 1 và 2 KH cùng trigger | Race condition | Concurrent assign | Chỉ 1 KH nhận. KH thứ 2 → pending. SELECT FOR UPDATE | P0 |
| E-303 | Pool có voucher expired | voucher có expires_at < today | Pop từ pool | FIFO theo expires_at — voucher hết hạn sớm nhất pop trước. Nhưng nếu < today → skip + mark EXPIRED | P0 |
| E-304 | OP upload file duplicate code | File có code đã tồn tại | Upload | Reject toàn bộ batch + show duplicates | P0 |
| E-305 | OP upload file 0 row | File rỗng | Upload | Reject với message "file rỗng" | P1 |
| E-306 | OP upload file 100K rows | Large file | Upload | Process trong <5 min, không timeout | P1 |
| E-307 | OP upload file mệnh giá 250K | Không trong enum | Upload | Reject + show valid enum | P0 |
| E-308 | OP upload file expires_at = today | Hết hạn ngay | Upload | Reject với warning "voucher hết hạn" | P0 |
| E-309 | KH click "Nhận quà" 2 lần liên tiếp (double-tap) | Concurrent | Click | Activate 1 lần. Lần 2 noop, mở deeplink Urbox | P0 |
| E-310 | Urbox API down khi click Nhận quà | Urbox 5xx | Click | Show "Hệ thống đang bận, vui lòng thử lại sau", retry 1 phút | P0 |
| E-311 | Voucher đã activated nhưng KH click Nhận quà lại | Status = REDEEMING | Click | Mở Urbox page với code cũ (không cấp mới) | P0 |

---

## Phần 5 — Notification (UC-02, UC-03, UC-05)

| # | Scenario | Precondition | Action | Expected | Priority |
|---|---|---|---|---|---|
| E-401 | KH không có email | email = null | Email gửi | Skip email, log "no_email", các kênh khác vẫn gửi | P0 |
| E-402 | Email bounce | SMTP trả 5xx | Email gửi | Retry 3 lần × 1h gap. Sau 3 lần fail → log + alert OP | P1 |
| E-403 | KH không có Zalo OA subscribed | Zalo API trả "not_subscribed" | Zalo gửi | Skip, log, không retry | P1 |
| E-404 | Push noti gateway down (Firebase 5xx) | FCM down | Push gửi | Retry exponential backoff 1m, 5m, 30m | P1 |
| E-405 | KH cài app nhưng turn off noti permission | Push token valid nhưng OS-level noti off | Push gửi | Push gửi đến FCM, FCM trả delivered, OS không show. Accept loss | P2 |
| E-406 | KH login app ngày sinh nhật trước 9:00 | KH mở app 8:30 sáng | Popup | Không hiển thị popup vì chưa trigger. KH login lại sau 9:00 sẽ thấy | P1 |
| E-407 | KH login app trong giờ sinh nhật, có popup, KH bấm X (đóng) | Popup hiện | KH đóng | Popup không hiển thị lại trong cùng session, hiển thị lại session sau (cùng ngày) | P1 |
| E-408 | Email template render lỗi (KH name có ký tự đặc biệt) | Tên KH = "Nguyễn O'Brien" | Email render | Escape ký tự, không break HTML | P0 |
| E-409 | KH thay đổi email/phone giữa snapshot và send | T-1 snapshot có email A, T 09:00 KH update email B | Email gửi | Gửi đến email B (lấy real-time) hoặc A (lấy snapshot)? **Decision: real-time** | P1 |

---

## Phần 6 — Màn Quà của tôi (UC-06)

| # | Scenario | Precondition | Action | Expected | Priority |
|---|---|---|---|---|---|
| E-501 | KH chưa từng có quà | First time use | Mở tab Quà sinh nhật | Empty state với icon + message "Sinh nhật năm nay chưa đến" | P1 |
| E-502 | KH có 5 năm history quà | Đã nhận 5 quà các năm trước | Mở tab | Scroll list, mỗi quà 1 card, sort year DESC | P1 |
| E-503 | KH có quà pending | Status = "Đang chuẩn bị" | Mở tab | Hiển thị card với placeholder + CTA disabled | P0 |
| E-504 | KH offline khi mở tab | Mất mạng | Mở tab | Hiển thị cached data + banner "Mất kết nối" | P1 |
| E-505 | KH redeem thành công, nhưng webhook Urbox về chậm | Urbox webhook delay 5 phút | KH refresh tab | Status vẫn "Đang xử lý", sau 5 phút webhook về → "Đã nhận" | P1 |
| E-506 | KH redeem nhưng chưa quay lại app | Click Nhận quà ở Urbox app, đóng | App mở lại sau 1h | Status đã update qua webhook → "Đã nhận" | P1 |
| E-507 | Voucher hết hạn mà KH chưa redeem | Voucher expires_at < today | Mở tab | Card với label "Đã hết hạn", CTA disabled, không pop card mới | P0 |

---

## Phần 7 — MB-VIP whitelist (MBL-301)

| # | Scenario | Precondition | Action | Expected | Priority |
|---|---|---|---|---|---|
| E-601 | File whitelist 400 rows, 80 không match CIF | Mismatch | Upload | Apply 320 match, export 80 unmatched cho OP review | P0 |
| E-602 | KH MB-VIP đột ngột bị remove khỏi whitelist | Quarter update | Apply remove | Effective_to = today, KH tier compute lại theo APE → có thể giảm tier | P0 |
| E-603 | KH MB-VIP whitelist nhưng APE = 0đ + có HĐBH active | Edge | Compute tier | tier = MB_VIP (override) | P0 |
| E-604 | OP upload file sai (rollback) | Đã apply 50 changes | Click rollback | Revert 50 changes, audit log | P1 |
| E-605 | File MB-VIP duplicate CIF | 5 row có CIF = "CIF001" | Upload | Deduplicate trong file, log warn | P1 |

---

## Phần 8 — Compliance & Privacy (Section 7 BRD)

| # | Scenario | Precondition | Action | Expected | Priority |
|---|---|---|---|---|---|
| E-701 | KH yêu cầu right-to-access | Gọi CSKH xin xem PII | DPO export | Export CSV/PDF trong 72h | P0 |
| E-702 | KH yêu cầu opt-out gift | Settings → Privacy → toggle | Update consent | Gift_consent = FALSE, không trigger năm tới | P0 |
| E-703 | KH withdraw consent giữa năm sau khi đã trigger | Đã nhận voucher năm 2026 | Withdraw | Không rollback voucher năm 2026, không trigger 2027 | P1 |
| E-704 | KH yêu cầu xóa data (right-to-delete) | Gọi DPO | DPO process | Anonymize customer_id, giữ structural log (không hard delete vì legal hold 10 năm) | P0 |
| E-705 | Audit pii_transfer_log full | DPO query log | Query | Log có đủ: customer_id, recipient_system, fields, legal_basis, timestamp, IP | P0 |
| E-706 | Cross-border transfer (Urbox AWS Singapore) | Nếu Urbox host ngoài VN | Transfer | DPIA filed, Cục An ninh mạng notified per Đ.43 NĐ 13 | P0 |

---

## Phần 9 — Performance & Scalability

| # | Scenario | Precondition | Action | Expected | Priority |
|---|---|---|---|---|---|
| E-801 | Peak load 9:00 sáng (70 trigger) | Burst 70 events trong 1 phút | Trigger | Process all trong <3 phút, không lag | P1 |
| E-802 | Tết — 200 trigger trong ngày | Peak Tết | Trigger | Process all trong <30 phút | P1 |
| E-803 | Database connection exhausted | Connection pool full | Trigger | Queue events trong Kafka, retry khi pool có slot | P1 |
| E-804 | Urbox API timeout | Latency > 30s | Click Nhận quà | Show timeout message, retry 1 lần auto | P0 |

---

## Phần 10 — Security

| # | Scenario | Precondition | Action | Expected | Priority |
|---|---|---|---|---|---|
| E-901 | Forge customer_id trong API call | Hacker thử pattern customer_id khác | API call | 403 Forbidden, audit alert | P0 |
| E-902 | Voucher code leak | Code public trên forum | Urbox redeem | Theo BR-12 voucher chỉ activate khi MBL allow click → mitigate | P0 |
| E-903 | App chạy trên thiết bị root | Detection trigger | KH mở app | Show warning per Vũ-Trang A9, không block | P1 |
| E-904 | SSL pinning bypass | Hacker MITM | Network call | App reject connection | P0 |

---

## Statistics

| Total cases | P0 | P1 | P2 |
|---|---|---|---|
| **89** | **52** | **34** | **3** |

QA effort estimate: ~25-30 SP cho test plan + execution. Auto-test cover: P0 100%, P1 60%.
