# User Stories + Acceptance Criteria — Quà sinh nhật

**Doc**: BA-DEL-01
**Author**: Trang (BA Lead)
**Date**: 2026-05-04
**Version**: 1.0
**Status**: Ready for grooming W19

**Phạm vi**: Các user stories cover UC-01 → UC-09 trong BRD Quà sinh nhật v0.3.

**DoR (Definition of Ready)**:
- ✅ AC viết theo BDD (Given/When/Then)
- ✅ Mỗi story có effort estimate placeholder cho team
- ✅ Cross-link với UC ID trong BRD
- ✅ Persona rõ ràng

**Persona reference**:
- **P1 — KH MB Life Style App** (cá nhân, BMBH, đã active app)
- **P2 — KH MB Life Style App** (cá nhân, BMBH, chưa active app — chỉ nhận email/SMS/zalo)
- **P3 — OP/Marketing** (admin, manage voucher pool)
- **P4 — CSKH agent** (CRM, xử lý complaint)
- **P5 — DPO** (audit PII transfer)

---

## Epic: MBL-EP-001 — Quà sinh nhật giai đoạn 1 (evoucher)

### MBL-101 — Đồng bộ thông tin KH + classify tier

**As a** Customer Care Service (system)
**I want to** đồng bộ daily thông tin KH từ DWH và phân hạng theo APE + MB-VIP whitelist
**So that** mỗi KH có tier chính xác cho event sinh nhật

**Story Points**: 8
**UC reference**: UC-01
**Dependencies**: DWH team confirm format file (action A3); whitelist MB-VIP module (action B5)

#### Acceptance Criteria

**AC1 — Happy path: Sync thành công với KH mới**
- **Given** DWH push file batch lúc 02:00 với 100 customer records mới (chưa có trong DB MBL)
- **When** Customer Care Service consume + validate
- **Then**:
  - Tất cả 100 records insert vào bảng `customer`
  - Field `customer_tier` được compute đúng theo BR-UC01-05
  - Audit log job run với status SUCCESS

**AC2 — Update customer existing**
- **Given** DWH push file với 50 records đã tồn tại (cùng customer_id)
- **When** Customer Care Service process
- **Then**:
  - 50 records UPDATE chỉ những field có value mới (không null)
  - Field null trong batch không ghi đè giá trị hiện tại
  - `last_synced_at` được update

**AC3 — MB-VIP whitelist override**
- **Given** KH `CUS001` có APE = 30 triệu (theo logic = Tiêu chuẩn) và `customer_id` của KH có trong `mb_vip_whitelist`
- **When** compute tier
- **Then** `customer_tier = 'MB_VIP'` (override APE rule)

**AC4 — KH chết: exclude**
- **Given** KH có `is_deceased = TRUE` từ DWH
- **When** sync
- **Then**:
  - KH vẫn được lưu trong DB (audit trail)
  - Field `is_deceased` = TRUE
  - Không trigger event sinh nhật trong các UC sau (BR-UC01-06)

**AC5 — Validation fail**
- **Given** record có `date_of_birth = NULL` hoặc format invalid
- **When** sync
- **Then**:
  - Record reject, log vào `sync_error_log` với reason
  - Không break các record khác trong batch
  - Nếu >5% batch fail validation → alert SRE + OP

**AC6 — Idempotency**
- **Given** job retry do network blip (cùng batch chạy lại)
- **When** sync lần 2
- **Then** dataset cuối cùng giống hệt lần 1, không duplicate, không có side effect

---

### MBL-102 — Compute snapshot tier tại T-1 sinh nhật

**As a** Customer Care Service
**I want to** snapshot tier của KH 1 ngày trước sinh nhật và lock value
**So that** event sinh nhật dùng đúng tier không bị ảnh hưởng bởi APE biến động trong ngày T

**Story Points**: 5
**UC reference**: UC-01 (BR-UC01-09)

#### Acceptance Criteria

**AC1 — Snapshot đúng giờ**
- **Given** KH X có DOB = 2026-05-05, hôm nay là 2026-05-04 (T-1)
- **When** snapshot job chạy lúc 02:30
- **Then**:
  - Bảng `customer_tier_snapshot` insert 1 record với (customer_id=X, event_date=2026-05-05, tier=<computed>, snapshot_at=2026-05-04 02:30)
  - Tier được compute theo BR-UC01-05 với APE tại moment snapshot

**AC2 — Lock không đổi trong ngày T**
- **Given** KH X đã snapshot là Bạc tại T-1, ngày T (sinh nhật) APE bỗng tăng lên Vàng do HĐ mới phát hành
- **When** event sinh nhật trigger lúc 09:00
- **Then** tier áp dụng = Bạc (theo snapshot), không phải Vàng

**AC3 — Sinh 29/2 năm thường**
- **Given** KH có DOB = 2000-02-29, hiện tại là 2026 (không nhuận)
- **When** snapshot job chạy
- **Then** snapshot record tạo cho event_date = 2026-02-28 (BR-UC01-07)

---

### MBL-103 — Trigger event sinh nhật + assign voucher

**As a** Loyalty Service
**I want to** subscribe event birthday_triggered và assign voucher từ pool theo tier
**So that** KH nhận được link evoucher đúng mệnh giá

**Story Points**: 13
**UC reference**: UC-07 (mới — Cấp & quản lý link Urbox)
**Dependencies**: Voucher pool schema (A4)

#### Acceptance Criteria

**AC1 — Happy path Bạc**
- **Given** KH X có tier=Bạc trong snapshot, event_date = today, pool tier Bạc còn 100 link
- **When** Loyalty Service consume birthday_triggered
- **Then**:
  - Pop 1 link từ pool (status AVAILABLE → ASSIGNED)
  - Insert `gift_assignment` record (customer_id=X, voucher_code=<code>, tier=Bạc, assigned_at=now())
  - Publish event `gift_assigned` với deeplink

**AC2 — Idempotency**
- **Given** event birthday_triggered cùng (customer_id, event_year) replay 2 lần
- **When** Loyalty consume cả 2
- **Then** chỉ 1 voucher được assign. Lần 2 skip + log "already assigned"

**AC3 — Pool out-of-stock fallback**
- **Given** pool tier Vàng = 0 links available
- **When** trigger với KH tier Vàng
- **Then**:
  - Insert `gift_assignment_pending` record với reason "pool_empty"
  - Publish event `gift_pending` (Notification Service handle differently — gửi message "Quà của Quý khách đang được chuẩn bị")
  - Alert SRE + OP qua PagerDuty
  - Retry sau 24h (D6)

**AC4 — KH Tiêu chuẩn không assign voucher**
- **Given** KH X có tier=Tiêu chuẩn
- **When** trigger
- **Then**:
  - Loyalty Service không assign voucher
  - Publish event `gift_skipped` với reason "tier_not_eligible"
  - Notification Service handle = gửi chúc mừng wording cũ (no CTA)

**AC5 — KH opt-out**
- **Given** KH X có `gift_opt_out = TRUE`
- **When** trigger
- **Then** publish `gift_skipped` với reason "opt_out", không assign voucher kể cả tier Vàng/KC/MB-VIP

---

### MBL-104 — Push notification + popup ngày sinh nhật

**As a** P1 (KH active app)
**I want to** nhận push notification + popup chúc mừng + CTA nhận quà vào ngày sinh nhật
**So that** tôi cảm thấy được quan tâm + nhận quà evoucher

**Story Points**: 8
**UC reference**: UC-03, UC-04

#### Acceptance Criteria

**AC1 — Push noti tier ≥Bạc**
- **Given** KH tier Bạc, ngày sinh nhật, pool có link sẵn
- **When** 09:00 sáng
- **Then**:
  - Push noti với content: *"🎉 Chúc Mừng Sinh Nhật Quý Khách 🎉 👉 Chạm để nhận quà ngay từ MB Life"*
  - Click → deeplink mở app → màn "Quà của tôi" → mục Quà sinh nhật

**AC2 — Push noti tier Tiêu chuẩn**
- **Given** KH tier Tiêu chuẩn
- **When** 09:00 sáng
- **Then**:
  - Push noti với content cũ: *"🎂 MB Life chúc mừng sinh nhật Quý Khách [Tên]. 🎉..."*
  - **Không** có CTA nhận quà
  - Click → mở app vào trang chủ

**AC3 — Popup khi mở app**
- **Given** KH đã login app, ngày sinh nhật
- **When** open app từ noti hoặc bình thường
- **Then**:
  - Popup hiển thị với confetti animation
  - Wording theo tier (per Excel R10, R11, R12)
  - Click "Nhận quà ngay" → màn Quà của tôi

**AC4 — KH chưa login**
- **Given** KH bấm push noti nhưng session expired
- **When** điều hướng vào app
- **Then**:
  - Theo luồng login chung MBAL Style 2025
  - Sau khi login → vào thẳng màn Quà của tôi (không qua trang chủ)

**AC5 — KH login lần 2 trong ngày**
- **Given** KH đã xem popup buổi sáng
- **When** login lại buổi chiều
- **Then** popup không hiển thị lại trong cùng ngày

---

### MBL-105 — Email + Zalo chúc mừng sinh nhật

**As a** P2 (KH chưa active app) hoặc P1
**I want to** nhận email/zalo chúc mừng sinh nhật + CTA nhận quà
**So that** tôi nhận được thông báo qua các kênh quen dùng

**Story Points**: 5
**UC reference**: UC-02 (modified), UC-05

#### Acceptance Criteria

**AC1 — Email tier ≥Bạc**
- **Given** KH tier Bạc, có email valid
- **When** 09:00 sinh nhật
- **Then**:
  - Email gửi với template R12 (Excel) — cá nhân hóa tên KH
  - QR code download MB Life Style App ở chân email
  - CTA "Nhận quà tại 'Quà của tôi'" trỏ về deeplink app

**AC2 — Email tier Tiêu chuẩn**
- **Given** KH tier Tiêu chuẩn
- **When** 09:00
- **Then** email với template cũ (BRD UC-05), không có CTA quà

**AC3 — Zalo tier ≥Bạc**
- **Given** KH có Zalo OA subscribed
- **When** 09:00
- **Then** Zalo message với template R13, button "Nhận quà ngay" → deeplink

**AC4 — SMS bị remove**
- **Given** KH bất kỳ tier
- **When** sinh nhật
- **Then** **không gửi SMS** (per Excel R14)

**AC5 — Email bounce / Zalo unsubscribed**
- **Given** email KH bounce hoặc Zalo OA chưa subscribe
- **When** gửi
- **Then**:
  - Notification Service log status FAILED với reason
  - Retry policy: email 3 lần × 1h gap, zalo 1 lần (không retry vì Zalo không có gateway error rõ)
  - Báo cáo daily cho OP để follow-up KH

---

### MBL-106 — Màn "Quà của tôi" — Quà sinh nhật

**As a** P1
**I want to** xem mục Quà sinh nhật trong màn Quà của tôi với đầy đủ thông tin
**So that** tôi quyết định khi nào nhận quà

**Story Points**: 8
**UC reference**: UC-06 (mới)

#### Acceptance Criteria

**AC1 — Hiển thị info quà sẵn sàng nhận**
- **Given** KH tier Bạc đã được assign voucher, chưa redeem
- **When** mở màn Quà của tôi → tab Quà sinh nhật
- **Then** hiển thị card với:
  - Loại: "evoucher"
  - Hạn sử dụng (theo D1 — activate-time + 6 tháng)
  - Giá trị: 150.000đ
  - Ngày tặng: <birthday>
  - Status: "Chưa nhận quà"
  - Button "Nhận quà"

**AC2 — Click Nhận quà**
- **Given** KH chưa redeem
- **When** click "Nhận quà"
- **Then**:
  - Mở deeplink Urbox (in-app browser)
  - Activate voucher tại Urbox (start clock 6 tháng)
  - Update local status = "Đang xử lý" → sau khi Urbox webhook về → "Đã nhận"

**AC3 — Quà đang chuẩn bị (pool empty)**
- **Given** KH có `gift_assignment_pending`
- **When** mở tab
- **Then** hiển thị "Quà của Quý khách đang được chuẩn bị, vui lòng kiểm tra lại trong 24h" + thông tin liên hệ CSKH

**AC4 — KH Tiêu chuẩn**
- **Given** KH tier Tiêu chuẩn
- **When** mở tab Quà sinh nhật
- **Then** hiển thị "Cảm ơn Quý khách đã đồng hành cùng MB Life. Hiện chưa có quà sinh nhật năm nay" — không có CTA

**AC5 — Lịch sử quà**
- **Given** KH đã nhận quà các năm trước
- **When** mở tab
- **Then** hiển thị list các quà theo năm, scroll xem lại

---

### MBL-107 — Pre-birthday communication T-7 (UC-09)

**As a** P1, P2 — KH Tiêu chuẩn năm 2025 đã nhận 50K
**I want to** nhận thông báo trước 7 ngày về thay đổi chương trình quà 2026
**So that** tôi không bị shock + hiểu chương trình mới

**Story Points**: 3
**UC reference**: UC-09 (mới — D4)

#### Acceptance Criteria

**AC1 — Trigger T-7 KH eligible**
- **Given** KH tier Tiêu chuẩn năm 2026 + có history nhận 50K năm 2025 + chưa nhận pre-birthday email năm nay
- **When** T-7 (job 09:00 ngày sinh nhật - 7)
- **Then** gửi 1 email từ Marketing template (W20 deliverable B8)

**AC2 — Trigger 1 lần lifecycle**
- **Given** KH đã nhận pre-birthday email năm 2026
- **When** năm 2027 cùng KH vẫn Tiêu chuẩn
- **Then** **không** gửi pre-birthday email (chỉ năm đầu chuyển đổi)

**AC3 — KH tier ≥Bạc không nhận**
- **Given** KH tier Bạc/Vàng/KC/MB-VIP
- **When** T-7
- **Then** không trigger UC-09

---

## Epic: MBL-EP-002 — Voucher Pool Management

### MBL-201 — Admin Portal upload voucher pool

**As a** P3 (OP)
**I want to** upload file Excel voucher từ Urbox vào pool MBL
**So that** voucher có sẵn để assign khi KH sinh nhật

**Story Points**: 5
**UC reference**: UC-07
**Dependencies**: B1 (Cường spec UI)

#### Acceptance Criteria

**AC1 — Upload happy path**
- **Given** OP có file Excel hợp lệ với 1.000 rows
- **When** upload qua Admin Portal
- **Then**:
  - System parse file, show preview với count theo mệnh giá
  - OP confirm → insert 1.000 records vào `voucher_pool` với status AVAILABLE
  - Audit log với (user, timestamp, file_hash, row_count)

**AC2 — Reject duplicate**
- **Given** file có 5 voucher_code trùng với pool hiện tại
- **When** upload
- **Then**:
  - Reject toàn bộ batch
  - Hiển thị list 5 codes trùng cho OP review

**AC3 — Reject invalid mệnh giá**
- **Given** file có row với face_value = 250.000 (không trong enum {150K, 200K, 500K, 1M, 2M})
- **When** upload
- **Then** reject batch + show error rõ ràng

**AC4 — Reject expires sớm**
- **Given** file có voucher với expires_at < today + 30 ngày
- **When** upload
- **Then** reject + warn "Voucher sắp hết hạn, không phù hợp nhập kho"

**AC5 — Permission**
- **Given** user không có role `OP_VOUCHER_MANAGER`
- **When** truy cập Admin Portal upload page
- **Then** 403 Forbidden + audit log

---

### MBL-202 — Pool monitoring dashboard

**As a** P3 (OP)
**I want to** xem dashboard pool status real-time
**So that** không bị out-of-stock bất ngờ

**Story Points**: 5
**Dependencies**: B2 (Vũ + Cường mock dashboard)

#### Acceptance Criteria

**AC1 — Hiển thị stock theo tier**
- **Given** pool có 3.000 Bạc / 800 Vàng / 150 KC / 50 MB-VIP
- **When** OP mở Grafana dashboard
- **Then** hiển thị 4 widgets stock theo tier với % so với safety stock 60 days

**AC2 — Forecast burn rate**
- **Given** sinh nhật 90 ngày tới: 250 Bạc, 80 Vàng, 18 KC, 5 MB-VIP
- **When** mở dashboard
- **Then** widget "days runway": Bạc 1080 days, Vàng 900 days, KC 750 days, MB-VIP 1000 days

**AC3 — Alert <30 days runway**
- **Given** pool Vàng còn 20 link, forecast 30 ngày tới = 25 link
- **When** check
- **Then** alert PagerDuty + email tới OP với subject "Voucher pool Vàng < 30 days"

---

## Epic: MBL-EP-003 — MB-VIP Whitelist

### MBL-301 — Upload MB-VIP whitelist

**As a** P3 (OP / đầu mối Tri ân)
**I want to** upload file MB-VIP từ MB Bank vào hệ thống
**So that** KH MB Private được nhận quà MB-VIP tier bất kể APE

**Story Points**: 5
**UC reference**: D3
**Dependencies**: B5, B6 (CIF mapping confirm), B7 (đầu mối)

#### Acceptance Criteria

**AC1 — Upload + lookup CIF**
- **Given** file Excel với 400 rows, mỗi row có CIF MB Bank
- **When** upload
- **Then**:
  - Job lookup CIF → customer_id MBL qua DWH
  - Filter chỉ giữ KH có HĐBH active
  - Diff với whitelist hiện tại

**AC2 — Apply changes**
- **Given** diff: 50 add, 10 remove
- **When** OP confirm
- **Then**:
  - 50 customer_id thêm vào `mb_vip_whitelist` với effective_from = today
  - 10 customer_id mark effective_to = today (soft delete)
  - Audit log từng thay đổi với source_ref + reason

**AC3 — Unmatched CIF**
- **Given** 80 CIF không tìm thấy match qua DWH
- **When** sau 3 retry (1 tuần)
- **Then**:
  - Export file CSV "unmatched_cifs.csv" cho OP review manual
  - Email OP với link download

**AC4 — Rollback**
- **Given** OP phát hiện file bị lỗi sau khi đã apply
- **When** click Rollback batch
- **Then** revert toàn bộ thay đổi của batch đó, log rollback action

---

## Epic: MBL-EP-004 — CSKH & Compliance

### MBL-401 — CRM lookup gift status

**As a** P4 (CSKH agent)
**I want to** lookup tình trạng quà sinh nhật của KH khi họ gọi complaint
**So that** xử lý nhanh + chính xác

**Story Points**: 3
**UC reference**: B11 spec

#### Acceptance Criteria

**AC1 — GET lịch sử quà**
- **Given** KH X gọi tổng đài complaint không nhận được quà
- **When** CSKH agent search customer_id X trong CRM portal
- **Then** hiển thị section "Lịch sử quà sinh nhật": list các năm + voucher_code + status (assigned/redeemed/expired/pending)

**AC2 — Regenerate link**
- **Given** voucher KH bị Urbox confirm lỗi
- **When** CSKH agent click "Cấp lại link" + chọn reason + manager approve (digital)
- **Then**:
  - Pool pop 1 link mới cùng tier
  - Link cũ mark `revoked`
  - KH nhận push noti "Link quà đã được cấp lại"
  - Audit log với agent_id, manager_id, reason

---

### MBL-402 — DPO admin API — PII transfer log

**As a** P5 (DPO)
**I want to** export PII transfer log của một KH khi họ exercise right-to-access
**So that** trả lời KH trong 72h theo Đ.16 NĐ 13

**Story Points**: 3
**UC reference**: A7

#### Acceptance Criteria

**AC1 — Export log**
- **Given** KH X gửi yêu cầu right-to-access qua kênh CSKH
- **When** DPO query qua admin API `/api/dpo/pii-transfer-log/{customer_id}`
- **Then**:
  - Trả CSV/PDF với toàn bộ records `pii_transfer_log` của KH X
  - Columns: timestamp, recipient_system, fields_transferred, legal_basis, purpose

**AC2 — Withdraw consent**
- **Given** KH yêu cầu withdraw consent gift
- **When** DPO PATCH `/api/dpo/customer/{id}/consent` với gift=false
- **Then**:
  - Field `gift_consent_active = FALSE`
  - Stop trigger các event sinh nhật năm tới (không rollback năm hiện tại nếu đã trigger)
  - Audit log

---

## Summary

| Epic | Stories | Total SP |
|---|---|---:|
| MBL-EP-001 (Quà sinh nhật core) | 7 | 50 |
| MBL-EP-002 (Voucher Pool) | 2 | 10 |
| MBL-EP-003 (MB-VIP Whitelist) | 1 | 5 |
| MBL-EP-004 (CSKH + Compliance) | 2 | 6 |
| **Total** | **12** | **71 SP** |

Estimate ~3-4 sprints với team velocity ~20 SP/sprint.
