# UAT Scenarios — Quà sinh nhật

**Doc**: BA-DEL-06
**Author**: Trang (BA Lead)
**Date**: 2026-05-04
**Version**: 1.0
**Audience**: PO (Thuỳ Giang), OP (Hương), Marketing, DPO — sign-off trước go-live.

**Mục đích**: Kịch bản UAT business stakeholders chạy thử trước go-live. Mỗi scenario là 1 luồng end-to-end thực tế, không phải unit test. Pass = stakeholder accept; Fail = block release.

**UAT environment**: `staging.mblife.vn` với Urbox sandbox.

**Test data prep**:
- 6 KH test với DOB = ngày UAT (tier khác nhau): T1 (Tiêu chuẩn 30tr), T2 (Bạc 75tr), T3 (Vàng 200tr), T4 (Kim cương 500tr), T5 (MB-VIP whitelist + APE 25tr), T6 (Tiêu chuẩn 30tr với history nhận 50K năm 2025).
- 1 KH chết: T7 (is_deceased=TRUE).
- 1 KH opt-out: T8 (gift_opt_out=TRUE).

---

## Scenario UAT-01 — KH Bạc nhận quà thành công (Happy Path)

**Persona**: P1 — KH active app
**Stakeholder owner**: Hương (OP)
**Priority**: P0
**Estimated time**: 20 phút

### Steps

1. **Trang setup**: Tạo customer T2 (DOB = today, tier=Bạc, đã active app).
2. **Pre-conditions verify**:
   - DWH đã sync T2 vào DB.
   - Snapshot T-1 đã chạy với tier=Bạc.
   - Pool tier Bạc còn ≥10 link.
3. **09:00 sáng**: Đợi/trigger manual job.
4. **Kiểm tra noti**:
   - Push noti hiện trên thiết bị test với content "🎉 Chúc Mừng Sinh Nhật...👉 Chạm để nhận quà ngay từ MB Life".
   - Email gửi đến (kiểm trong inbox test).
   - Zalo OA message gửi đến (test account).
5. **KH tap push** → app mở → popup hiển thị với:
   - Tên KH cá nhân hóa ("Quý khách [Tên T2]").
   - Animation confetti chạy.
   - Button "Nhận quà ngay".
6. **Tap "Nhận quà ngay"** → màn Quà của tôi → tab Quà sinh nhật → card hiển thị:
   - "Quà sinh nhật 2026"
   - Giá trị: 150.000đ
   - Status: Chưa nhận quà
   - Hạn sử dụng: 6 tháng (chưa active)
   - Button "Nhận quà"
7. **Tap "Nhận quà"** → mở Urbox sandbox → activate voucher → redirect catalogue.
8. **Quay lại app** sau 1 phút → status update thành "Đã nhận quà".

### Pass criteria
- Tất cả 8 steps thực hiện được.
- Email content khớp template R12.
- Zalo content khớp R13.
- Voucher pool count Bạc giảm 1.
- `pii_transfer_log` có entry với fields = ["customer_id", "face_value"].

### Sign-off
- [ ] Hương (OP)
- [ ] Thuỳ Giang (PO)
- [ ] Duy (Designer) — UX visual

---

## Scenario UAT-02 — KH Tiêu chuẩn (không nhận quà) — chuyển đổi từ 2025

**Persona**: P1 (T6 — đã nhận 50K năm 2025)
**Stakeholder owner**: Marketing + Hương
**Priority**: P0
**Estimated time**: 15 phút

### Steps

1. **Setup**: T6 với DOB=today, tier=Tiêu chuẩn, history `received_gift_50k_2025=TRUE`.
2. **T-7**: Verify email pre-birthday gửi đến T6 với content giải thích chương trình thay đổi.
3. **T 09:00**: Trigger.
4. **Kiểm tra**:
   - Push noti với wording cũ: "🎂 MB Life chúc mừng sinh nhật...".
   - **Không** có CTA "Nhận quà".
   - Email với template cũ.
   - **Không** có SMS (BR).
5. **Mở app** → popup wording cũ → tap đóng.
6. **Vào màn Quà của tôi** → tab Quà sinh nhật → empty state: "Cảm ơn Quý khách...Hiện chưa có quà sinh nhật năm nay".

### Pass criteria
- T6 không nhận voucher (gift_assignment.status=SKIPPED, reason=tier_not_eligible).
- Pre-birthday email gửi T-7 đúng template.
- Không có SMS gửi.

### Sign-off
- [ ] Marketing (FAQ + email content reviewed)
- [ ] Hương
- [ ] PO Thuỳ Giang — confirm "no death zone" decision

---

## Scenario UAT-03 — KH MB-VIP override APE thấp

**Persona**: T5 (whitelist + APE 25tr)
**Stakeholder owner**: Hương + Marketing
**Priority**: P0
**Estimated time**: 15 phút

### Steps

1. **Setup**: T5 với APE=25tr, customer_id IN mb_vip_whitelist.
2. Verify snapshot T-1: tier=MB_VIP (override).
3. **T 09:00 trigger**.
4. **Kiểm tra**:
   - Push noti với CTA Nhận quà.
   - Tap → popup → màn Quà của tôi → card với value = MB-VIP value (theo Marketing chốt).

### Pass criteria
- Tier hiển thị MB_VIP dù APE chỉ 25tr.
- Value voucher đúng theo Marketing config.
- Audit log có flag `mb_vip_override = TRUE`.

### Sign-off
- [ ] Hương (vận hành)
- [ ] Marketing (value)

---

## Scenario UAT-04 — KH chết trước sinh nhật

**Persona**: T7 (is_deceased=TRUE)
**Stakeholder owner**: DPO + PO
**Priority**: P0
**Estimated time**: 10 phút

### Steps

1. **Setup**: T7 với is_deceased=TRUE từ DWH.
2. **T 09:00 trigger**.
3. **Kiểm tra**:
   - **Không** có push noti gửi đến T7.
   - **Không** có email/zalo.
   - Bảng `gift_assignment` không có record cho T7.
   - Audit log có entry "skipped_deceased".

### Pass criteria
- 100% silent — không có touchpoint nào với T7.
- Audit trail đầy đủ (DPO requirement).

### Sign-off
- [ ] DPO
- [ ] PO Thuỳ Giang — reputation safety

---

## Scenario UAT-05 — KH chết sau khi đã trigger (rollback)

**Persona**: T2 sau khi trigger thành công
**Stakeholder owner**: DPO
**Priority**: P0
**Estimated time**: 20 phút

### Steps

1. **Setup**: Replicate UAT-01 với T2, KH đã nhận push noti, **chưa** click Nhận quà.
2. **Mock DWH update**: T2 với is_deceased=TRUE batch hôm sau (T+1).
3. **Sync chạy** → CC detect change.
4. **Kiểm tra**:
   - Voucher T2 đã assign mark status=REVOKED.
   - Email chuỗi sau (nếu có) bị stop.
   - Audit log có entry "deceased_post_trigger".
   - Không gửi voucher cho người thân.

### Pass criteria
- Rollback chạy trong 24h từ DWH detect.
- Voucher không recoverable.

### Sign-off
- [ ] DPO
- [ ] Pháp chế (legal hold validation)

---

## Scenario UAT-06 — Out-of-stock fallback

**Persona**: T3 (Vàng) khi pool Vàng = 0
**Stakeholder owner**: Hương + Cường
**Priority**: P0
**Estimated time**: 30 phút

### Steps

1. **Setup**: Drain pool Vàng về 0 (manual SQL trên staging).
2. **T 09:00 trigger** với T3.
3. **Kiểm tra noti**:
   - Push: "Quà của Quý khách đang được chuẩn bị, vui lòng kiểm tra lại trong 24h".
   - PagerDuty alert đến OP.
4. **Vào màn Quà của tôi**:
   - Card với placeholder "Đang chuẩn bị quà".
   - CTA disabled.
5. **OP rush procurement**: upload batch 20 link Vàng qua Admin Portal.
6. **Đợi 24h** (hoặc trigger retry job manual):
   - Voucher pop, gift_assignment update ASSIGNED.
   - Push noti mới: "Quà của Quý khách đã sẵn sàng".

### Pass criteria
- KH luôn nhận chúc mừng (graceful degradation).
- Retry chạy đúng 24h.
- Không downgrade tier.

### Sign-off
- [ ] Hương (operations)
- [ ] Cường (technical)

---

## Scenario UAT-07 — KH opt-out gift

**Persona**: T8 (Vàng nhưng opt-out)
**Stakeholder owner**: DPO
**Priority**: P1
**Estimated time**: 15 phút

### Steps

1. **Setup**: T8 tier=Vàng, gift_opt_out=TRUE.
2. **T 09:00 trigger**.
3. **Kiểm tra**:
   - Push noti chúc mừng (wording cũ, không CTA).
   - Email chúc mừng.
   - **Không** có voucher assign.
4. **Mở app** → màn Quà của tôi → empty state.
5. **Settings → Privacy**: KH có thể tắt/bật toggle "Nhận quà sinh nhật" → audit log capture change.

### Pass criteria
- KH vẫn nhận chúc mừng (BR-13).
- KH không bị skip toàn bộ touchpoint.
- Toggle settings work.

### Sign-off
- [ ] DPO
- [ ] Duy (UX settings page)

---

## Scenario UAT-08 — KH yêu cầu DPO export PII transfer log

**Persona**: P5 — DPO
**Stakeholder owner**: DPO
**Priority**: P0
**Estimated time**: 15 phút

### Steps

1. **Setup**: T2 đã hoàn thành flow UAT-01 (đã transfer data sang Urbox).
2. **DPO login admin portal**.
3. **Query**: customer_id = T2 → tab "PII transfer history".
4. **Kiểm tra**:
   - List tất cả pii_transfer_log entries của T2.
   - Columns đầy đủ: timestamp, recipient_system, fields, legal_basis, purpose, request_id.
5. **Export CSV/PDF** → download file.
6. **Verify file**: structure đúng, KH có thể đọc hiểu.

### Pass criteria
- Export hoàn thành trong <30s.
- Đầy đủ thông tin theo NĐ 13 Đ.16.
- Có cách deliver cho KH (email attach hoặc upload secure portal).

### Sign-off
- [ ] DPO
- [ ] Pháp chế

---

## Scenario UAT-09 — KH withdraw consent giữa năm

**Persona**: T2 sau khi đã nhận quà 2026
**Stakeholder owner**: DPO
**Priority**: P1
**Estimated time**: 20 phút

### Steps

1. **Setup**: T2 đã nhận quà UAT-01.
2. **App Settings → Privacy → Toggle "Nhận quà sinh nhật" OFF**.
3. **Verify**:
   - `customer_consent.granted=FALSE`, `withdrawn_at=now()`.
   - Voucher 2026 đã activate **không bị recall** (theo DPO decision).
4. **Mock T2 sinh nhật năm 2027**: trigger.
5. **Verify**:
   - Không assign voucher 2027.
   - Vẫn gửi chúc mừng (theo BR-13).

### Pass criteria
- Withdraw effective từ năm sau.
- Voucher năm hiện tại không bị mất.

### Sign-off
- [ ] DPO

---

## Scenario UAT-10 — Pool monitoring + alert

**Persona**: P3 — OP
**Stakeholder owner**: Hương + Cường
**Priority**: P1
**Estimated time**: 30 phút

### Steps

1. **Open Grafana dashboard** "Voucher Pool Status".
2. **Verify**: 4 widgets stock theo tier (Bạc/Vàng/KC/MB-VIP).
3. **Mock pool Vàng giảm xuống 20 link** (forecast 30 ngày = 25 link → runway < 30 days).
4. **Trigger alert job**.
5. **Verify**:
   - PagerDuty/Email alert tới OP với subject "Voucher pool VANG < 30 days runway".
   - Dashboard widget chuyển màu vàng/đỏ.

### Pass criteria
- Alert delivery <5 phút.
- OP có thể action ngay (link tới Admin Portal upload).

### Sign-off
- [ ] Hương
- [ ] Cường

---

## Scenario UAT-11 — Upload voucher pool file

**Persona**: P3 — OP
**Stakeholder owner**: Hương
**Priority**: P0
**Estimated time**: 25 phút

### Steps

1. **OP login Admin Portal** → menu Voucher Pool → Upload.
2. **Test upload happy path**: file Excel 100 rows hợp lệ.
3. **Verify**:
   - Preview hiển thị count theo mệnh giá.
   - OP confirm → 100 records insert thành công.
4. **Test reject duplicate**: file có 5 codes trùng pool hiện tại → reject toàn bộ batch.
5. **Test reject mệnh giá invalid**: face_value=250K → reject.
6. **Test reject expires sớm**: expires_at < today+30 ngày → reject.
7. **Test rollback**: sau khi upload thành công 100 records, OP click Rollback batch → 100 records remove (audit log capture).

### Pass criteria
- 4 test cases pass.
- UI feedback rõ ràng (success/error messages).

### Sign-off
- [ ] Hương — UX usability

---

## Scenario UAT-12 — MB-VIP whitelist quarterly update

**Persona**: P3 — OP / Tri ân
**Stakeholder owner**: Hương
**Priority**: P0
**Estimated time**: 30 phút

### Steps

1. **OP nhận file Excel MB Bank** với 400 CIF.
2. **Upload qua Admin Portal**.
3. **Verify**:
   - Job lookup CIF → customer_id qua DWH.
   - Filter chỉ giữ KH có HĐBH active.
   - Show preview: 320 match, 80 unmatched.
4. **OP confirm apply changes**.
5. **Verify**:
   - 50 add, 10 remove (nếu có change so với whitelist hiện tại).
   - Audit log từng change.
6. **Verify export unmatched**:
   - 80 CIF chưa match được export ra CSV cho OP review manual.

### Pass criteria
- Lookup chạy đúng.
- Audit trail đầy đủ.

### Sign-off
- [ ] Hương + đầu mối Tri ân

---

## Summary

| UAT | Scenario | Priority | Owner |
|---|---|---|---|
| UAT-01 | KH Bạc happy path | P0 | Hương + PO |
| UAT-02 | KH Tiêu chuẩn không quà | P0 | Marketing + PO |
| UAT-03 | KH MB-VIP override | P0 | Hương + Marketing |
| UAT-04 | KH chết trước trigger | P0 | DPO + PO |
| UAT-05 | KH chết post-trigger | P0 | DPO + Pháp chế |
| UAT-06 | Out-of-stock fallback | P0 | Hương + Cường |
| UAT-07 | KH opt-out | P1 | DPO + Designer |
| UAT-08 | DPO export PII log | P0 | DPO + Pháp chế |
| UAT-09 | KH withdraw consent | P1 | DPO |
| UAT-10 | Pool monitoring alert | P1 | Hương + Cường |
| UAT-11 | Upload voucher pool | P0 | Hương |
| UAT-12 | MB-VIP whitelist update | P0 | Hương |

**Total**: 12 scenarios, ~3.5h execution time. UAT scheduled W22-W23 trước go-live W24.

---

## Sign-off matrix

UAT toàn bộ phải có chữ ký của:
- [ ] Thuỳ Giang (PO) — overall product readiness
- [ ] Hương (OP) — operations readiness
- [ ] Marketing — content readiness
- [ ] DPO — privacy compliance readiness
- [ ] Pháp chế — legal readiness
- [ ] Cave (PM/SM) — project readiness
- [ ] Vũ (SA) — technical readiness
- [ ] QA Lead — test coverage readiness

**Block release if any signoff missing**.
