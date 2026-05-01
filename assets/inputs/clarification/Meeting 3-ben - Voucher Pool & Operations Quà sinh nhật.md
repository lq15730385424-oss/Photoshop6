# Meeting 3-bên: Voucher Pool & Operations — Quà sinh nhật

**Date**: 2026-05-04 (Thứ 2, W19)
**Time**: 09:30–11:30 (120 min)
**Location**: MR.401 + Teams

**Attendees**:
- **Trang** — BA Lead, Squad 1 (facilitator + recorder)
- **Vũ** — Solution Architect
- **Cường** — IT Lead (Customer Care Service implementation)
- **Hương** — OP Lead (vendor & gift operations)

**Agenda**:
1. Quy trình hiện tại mua link Urbox (Hương)
2. Voucher pool model — fit với operations? (3 bên)
3. Volume forecast 2026 + budget breakdown (Hương)
4. MB-VIP whitelist sync từ MB tập đoàn (Hương + Cường)
5. KH năm 2025 đã nhận 50K — impact analysis (Hương)
6. Out-of-stock & lead time (3 bên)
7. Edge cases vận hành OP (3 bên)
8. Decisions + action items

---

## 1. Quy trình hiện tại mua link Urbox (Hương present)

**Hương (OP)**: Hiện tại OP đã có quan hệ với Urbox từ chương trình tri ân Q4/2025. Quy trình:

> **Quy trình hiện tại**:
> 1. OP gửi PO tới Urbox với mệnh giá + số lượng. VD: 1.000 link mệnh giá 200K.
> 2. Urbox confirm trong 2 ngày làm việc, gửi quote.
> 3. Sau khi MBL approve PO + thanh toán (NET 30), Urbox xuất batch trong 5 ngày làm việc.
> 4. Urbox gửi file Excel chứa N rows: `voucher_code`, `redeem_url`, `face_value`, `expires_at` — qua email OP.
> 5. OP forward file cho IT để nhập hệ thống. **Hiện tại OP đang nhập tay vào sheet Google.**
> 6. Khi cần phát quà manual (vd Tri ân Q4), OP query sheet, copy link, paste vào email cá nhân hoá gửi KH.

**Hương**: Quy trình thủ công, scale cho 25K KH/năm là không khả thi. Em mong tech tự hoá hoàn toàn từ bước 5.

**Trang**: Em note. Hương ơi, **hạn sử dụng của 1 link Urbox kể từ khi cấp** là bao lâu? Có config được không?

**Hương**: Default Urbox là **6 tháng** kể từ lúc xuất batch. Nếu cần dài hơn phải nói trước khi PO, có thể pay thêm phí. Em đề xuất giữ default 6 tháng cho Quà sinh nhật vì nếu KH không nhận trong 6 tháng từ ngày sinh nhật thì coi như KH không quan tâm.

**Cường (IT)**: Anh hỏi: "expires_at" trong file là tính từ ngày Urbox xuất hay từ ngày MBL gán cho KH? Khác nhau quan trọng.

**Hương**: Tính từ ngày Urbox xuất batch. Tức là nếu MBL nhập kho hôm nay, 6 tháng sau hết hạn — bất kể MBL có gán cho KH hay chưa.

**Vũ (SA)**: Đó là vấn đề. Nếu pool nhập đầu năm mà sinh nhật KH vào tháng 11 → KH chỉ có 1 tháng để redeem. **UX kém**.

> **Decision D1**: OP thương lượng Urbox về 1 trong 2 phương án:
> - (a) Hạn 12 tháng từ ngày xuất batch (đắt hơn nhưng đơn giản).
> - (b) Hạn 6 tháng nhưng tính từ **ngày MBL activate code** (KH self-redeem mới start clock).
> Hương lead, em deadline EOD W19.

**Hương**: OK em làm việc với Urbox. Em ưu tiên (b) vì cost không thay đổi nhiều — cơ chế kỹ thuật ở Urbox nên có sẵn.

---

## 2. Voucher pool model — fit operations?

**Vũ**: Anh present schema `voucher_pool` em đã design (xem meeting Trang-Vũ minutes A4). Concern chính: **interface Hương import file Excel của Urbox vào pool**.

**Cường**: Anh propose 2 options:
- **Option 1**: OP upload file Excel qua Admin Portal → Customer Care Service parse + insert. Có UI validation + preview trước commit.
- **Option 2**: API endpoint cho OP/IT gọi với file payload. CLI/Postman.

OP nên dùng Option 1 vì friendly hơn. Effort estimate: ~5 SP cho UI + 3 SP cho parser + validation. Tổng ~1 sprint.

**Hương**: Em prefer Option 1. Em không biết coding. Nhưng em hỏi: nếu file Urbox bị sai (vd duplicate code), hệ thống xử lý sao?

**Cường**: Validation rules anh đề xuất:
- Reject toàn bộ batch nếu có duplicate code (within file hoặc với pool hiện tại).
- Reject nếu mệnh giá không thuộc enum (150K/200K/500K/1tr).
- Reject nếu expires_at < today + 30 ngày (link sắp hết hạn — nhập làm gì).
- Show preview với row count theo mệnh giá trước khi commit.
- Audit log import action với user, timestamp, file hash.

**Trang**: Em note thêm — KH cần nhận quà phải có cơ chế **auto reconcile**: khi pool tier X < 30 days forecast → alert OP. Anh Vũ đã thiết kế trong A4. Hương có dashboard riêng để xem pool status, đúng không anh?

**Vũ**: Đúng, dashboard Grafana shared cho OP + Squad. Show:
- Pool remaining theo từng tier.
- Forecast burn rate (dựa vào số KH có DOB trong 30/60/90 ngày tới).
- Ngày dự kiến hết stock từng tier.
- Alert khi <30 days runway.

**Hương**: OK rất hay. Em không phải đoán nữa.

**Action item B1**: Cường spec UI Admin Portal upload voucher pool. Deadline: W19 grooming.
**Action item B2**: Vũ + Cường share Grafana mock với Hương trước W20. Hương feedback metric nào missing.

---

## 3. Volume forecast 2026 + budget breakdown

**Hương**: Em có data anh Cave hỏi rồi. Forecast 2026:

| Hạng | Số KH eligible (forecast 2026) | % base | Value/KH | Tổng budget/năm |
|---|---|---:|---:|---:|
| Tiêu chuẩn | ~480.000 | 95.0% | 0đ | 0đ |
| Bạc | ~18.500 | 3.7% | 150.000 | 2.775.000.000đ |
| Vàng | ~5.200 | 1.0% | 200.000 | 1.040.000.000đ |
| Kim cương | ~1.100 | 0.22% | 500.000 | 550.000.000đ |
| MB-VIP | ~350 | 0.07% | **? (Marketing chưa chốt)** | ? |

**Tổng base ước tính**: ~505.150 KH có HĐBH active đầu 2026.
**Budget 2026 đã được phê duyệt**: **5 tỷ** cho Quà sinh nhật + Quà kỷ niệm HĐ. Quà sinh nhật được phân bổ ~70% = **3.5 tỷ**.

**Trang**: Em tính nhanh: Bạc + Vàng + KC = 4.36 tỷ. **Đã vượt 3.5 tỷ**. Kể cả chưa tính MB-VIP. Hương xử lý sao?

**Hương**: Em đã raise với Finance. 2 hướng:
- (1) Xin thêm budget — Finance bảo "review giữa năm".
- (2) **Cap số KH/tháng** — phân bổ đều, KH sinh nhật cuối năm có rủi ro out-of-budget.

**Vũ**: Option (2) tạo unfair experience. Anh đề xuất hybrid:
- Reserve 60% budget cho first half (sinh nhật phân bổ uniform).
- 40% cho second half + buffer.
- Q3 review burn rate, nếu vượt → giảm value tier thấp 10-15% từ Q4.

**Hương**: OK em note. Em xin thêm: **MB-VIP 350 KH, chỉ 0.07% base nhưng là VIP** — đề xuất Marketing phân bổ riêng từ budget Tri ân thay vì gộp vào quà sinh nhật. Cost dù cao cũng nhỏ.

**Trang**: Em sẽ raise với chị Thuỳ Giang (PO) + Marketing khi review tuần tới.

> **Decision D2**: Cap budget hard 3.5 tỷ cho Quà sinh nhật (giai đoạn 1). MB-VIP carve-out ngân sách riêng. Q3/2026 review burn rate, có quyền điều chỉnh tier value.

**Action item B3**: Hương draft proposal điều chỉnh value nếu burn rate vượt 50% trước Q2 end. Deadline: 30/06/2026.
**Action item B4**: Trang raise MB-VIP carve-out với PO + Marketing. Deadline: W19.

---

## 4. MB-VIP whitelist sync từ MB tập đoàn

**Hương**: Em đã ping bộ phận Tri ân của MB Bank. Họ confirm:
- **Có** danh sách MB Private (gọi tên chính thức là "MB Private", chưa phải "MB-VIP" như mình đặt). **350-400 KH**, update **hàng quý** (tháng 1, 4, 7, 10).
- Source: MB Bank Wealth Management.
- Format: file Excel qua email tới đầu mối Tri ân của MBL.
- Key match: **CIF MB Bank**, không phải customer_id MBL.
- Họ KHÔNG có API.

**Cường**: CIF MB Bank không phải key của mình. Phải lookup CIF → customer_id MBL. Anh hỏi anh Vũ:

**Vũ**: Có 2 vấn đề:
1. **Mapping CIF → customer_id MBL**: cần qua DWH (DWH có cả 2 fields). Trang follow-up DWH team.
2. **KH MB Private có HĐBH MBL**: KHÔNG phải tất cả 350-400. Có thể chỉ 100-150 KH thực sự có HĐBH active.

> **Decision D3**: Pipeline MB-VIP whitelist:
> 1. Email từ MB Bank → đầu mối Tri ân MBL → upload file vào Customer Care Admin Portal (cùng UI với voucher pool, separate tab).
> 2. Customer Care Service: chạy job lookup CIF → customer_id qua DWH.
> 3. Filter: chỉ giữ customer_id có HĐBH active.
> 4. Diff với whitelist hiện tại, apply changes, audit log từng thay đổi.
> 5. Nếu CIF không tìm thấy match → flag "unmatched", export cho OP review manual.

**Hương**: OK em chấp nhận. Em concern: có khi CIF mới có HĐBH MBL nhưng DWH chưa sync. Có handle race condition không?

**Vũ**: Có. Job sẽ retry 3 lần mỗi tuần. Nếu sau 3 lần vẫn không match thì flag "pending" — không reject.

**Action item B5**: Cường implement MB-VIP whitelist import module (extends voucher pool module). Effort: ~3 SP. Deadline: W21.
**Action item B6**: Trang confirm DWH có CIF mapping field. Deadline: W19.
**Action item B7**: Hương identify chính thức **đầu mối Tri ân MBL** nhận file từ MB Bank. Deadline: W19.

---

## 5. KH năm 2025 đã nhận 50K — impact analysis

**Hương**: Em pull data 2025:
- KH đã nhận chúc mừng + quà 50K (theo BRD cũ): **~62.500 KH** — tức là APE 10tr–<100tr.
- **78%** là KH đã có >2 năm tham gia (loyalty cao).

**Trang**: 62.5K KH năm sau không nhận quà. Đó là số lớn. Risk complaint cao.

**Hương**: Em đã nói chuyện với CSKH manager. Họ predict ~0.3-0.5% gọi complaint = ~190-310 cuộc gọi trong 1 năm. Manageable nếu có script + truyền thông tốt.

**Vũ**: Suggestion technical: với KH đã nhận 50K năm 2025, **gửi email truyền thông trước sinh nhật 7 ngày** giải thích "chương trình quà đã thay đổi để tập trung vào KH có tổng giá trị cam kết cao hơn — chúc mừng vẫn đầy đủ". Tránh shock at moment of truth.

**Hương**: Hay. Marketing có thể prepare. Em xin Trang note thành requirement.

**Trang**: Em add UC mới — UC-09: Pre-birthday communication (Tiêu chuẩn-only). Trigger T-7. Trigger 1 lần đầu năm, không lặp.

> **Decision D4**: Bổ sung UC-09 — pre-birthday communication T-7 cho KH Tiêu chuẩn lần đầu trong năm 2026.

**Action item B8**: Trang draft UC-09 + Marketing draft email content. Deadline: W20.

---

## 6. Out-of-stock & lead time

**Hương**: Em xác nhận với Urbox về Tết + dịp lễ:
- **Lead time bình thường**: 7 ngày làm việc từ PO → giao file.
- **Lead time peak (Tết, 8/3, 20/10, Noel)**: 14 ngày.
- **Black-out period**: tuần sát Tết (5 ngày) — Urbox không xuất batch.

**Vũ**: Black-out period = vấn đề. Nếu MBL sinh nhật KH rơi vào tuần đó mà pool hết → fallback?

**Cường**: Anh đề xuất **safety stock**: pool tier mỗi mệnh giá luôn maintain stock ≥ peak forecast 60 ngày. Tức Bạc luôn có ≥3.000 link, Vàng ≥850, KC ≥180, MB-VIP ≥60.

**Hương**: Em sẽ điều chỉnh frequency mua: tháng 1 mua đủ Q1+Q2 thay vì hàng quý. Cost neutral.

> **Decision D5**: Safety stock policy — pool mỗi tier ≥60 days forecast. Order frequency: bi-monthly thay vì quarterly. Tết: order Tết+1 tuần extra.

**Action item B9**: Hương + Cường + Vũ tune alerting thresholds dựa trên safety stock. Deadline: W20.

**Trang**: Em hỏi follow-up: **nếu trong vận hành xảy ra out-of-stock thực sự** thì sao?

**Vũ**: Đây là R11 anh đã flag trong meeting Trang-Vũ. 3 lựa chọn:
- (a) **Delay 24h**: KH nhận chúc mừng "Quà của Quý khách đang được chuẩn bị, vui lòng kiểm tra lại trong 24h". OP rush mua Urbox + MBL re-trigger.
- (b) **Downgrade tier**: KH Vàng không có Vàng → tặng Bạc, kèm xin lỗi.
- (c) **Compensation alternative**: gửi voucher CSKH MBL (free check-up sức khoẻ, etc.).

**Hương**: Em thích (a). KH chấp nhận chờ 24h hơn là nhận quà thấp hơn expectation.

> **Decision D6**: Out-of-stock fallback = (a) Delay 24h + rush procurement. Customer Care Service tự động retry sau 24h.

**Action item B10**: Cường implement retry mechanism với queue `gift_assignment_pending`. Deadline: W22.

---

## 7. Edge cases vận hành OP

**Trang**: Em list các edge case từ Section 4 BRD update:

### 7.1 KH complaint không nhận được quà / link lỗi

**Hương**: Em đề xuất SOP:
1. KH gọi tổng đài CSKH → check trên CRM (CRM tích hợp Customer Care Service qua API).
2. CSKH thấy `gift_status` của KH → giải thích.
3. Nếu link bị lỗi (Urbox side), CSKH escalate lên OP → OP request Urbox cấp link mới.
4. SLA escalation: CSKH 24h, OP→Urbox 48h, total ≤72h.

**Cường**: CRM portal cần API Customer Care Service expose:
- GET `/api/customer-care/{customer_id}/gifts?year=2026` → lịch sử quà + status hiện tại.
- POST `/api/customer-care/{customer_id}/gifts/regenerate` → admin action cấp lại link.

**Vũ**: Audit log cho mỗi action regenerate. Lý do regenerate + manager approval cho action sensitive.

**Action item B11**: Cường spec CRM integration API. Deadline: W21.

### 7.2 KH từ chối nhận quà (tang chế, tôn giáo)

**Hương**: Hiếm nhưng có. OP có flag `gift_opt_out` ở CRM hiện tại. Cần migrate vào Customer Care Service.

**Trang**: Em note vào BR-UC01-10. Logic: `IF gift_opt_out = TRUE: vẫn gửi chúc mừng (không quà), mark sự kiện `gift_skipped` với reason `opt_out`.

### 7.3 Tax — quà ≥500K có khai TNCN không?

**Hương**: Em đã check Finance. Theo Luật TNCN: quà tặng từ tổ chức ≥10 triệu/lần phải khai. Quà sinh nhật mức cao nhất em forecast là MB-VIP 1tr-2tr → **không phải khai**. OK.

**Trang**: Em close mục B-22 trong Q&A list.

### 7.4 KH chết sau khi đã trigger quà (B-12a)

**Hương**: Em nói chuyện với pháp chế. **Không gửi link nhận quà cho người thân**. Lý do:
- Voucher Urbox không transferable theo T&C.
- KH có thể chưa chia di sản, voucher có giá trị nhưng nhỏ — không đáng trigger legal complications.

**Vũ**: Logic: `IF is_deceased = TRUE post-trigger: rollback voucher_assignment, return code to pool, mark customer event = "skipped_deceased"`. Audit + alert OP để follow-up người thân nếu cần.

> **Decision D7**: KH chết post-trigger → rollback voucher, không gửi người thân.

**Action item B12**: Cường implement rollback flow + Trang document SOP cho CSKH thông báo người thân nếu cần.

---

## 8. Decisions tổng hợp + Action items

### 8.1 Decisions chốt

| ID | Quyết định |
|---|---|
| D1 | Voucher Urbox: hạn 6 tháng từ ngày MBL **activate code** (Hương deal Urbox) |
| D2 | Cap budget hard **3.5 tỷ/năm**. MB-VIP carve-out ngân sách Tri ân riêng |
| D3 | MB-VIP whitelist via Excel email từ MB Bank → upload Admin Portal MBL → CIF lookup qua DWH |
| D4 | Bổ sung UC-09 — pre-birthday communication T-7 cho KH Tiêu chuẩn (1 lần lifecycle) |
| D5 | Safety stock pool tier ≥60 days forecast. Order bi-monthly + Tết extra |
| D6 | Out-of-stock fallback: delay 24h + rush procurement (không downgrade tier) |
| D7 | KH chết post-trigger: rollback voucher, không transfer cho người thân |

### 8.2 Action items

| ID | Task | Owner | Deadline |
|---|---|---|---|
| B1 | UI Admin Portal upload voucher pool — spec | Cường | W19 grooming |
| B2 | Grafana dashboard pool status mock cho Hương review | Vũ + Cường | W20 |
| B3 | Burn rate proposal điều chỉnh tier value | Hương | 30/06/2026 |
| B4 | Raise MB-VIP carve-out budget với PO + Marketing | Trang | W19 |
| B5 | MB-VIP whitelist import module (extends pool module) | Cường | W21 |
| B6 | Confirm DWH có CIF mapping field | Trang | W19 |
| B7 | Identify đầu mối Tri ân MBL nhận file MB Bank | Hương | W19 |
| B8 | UC-09 spec + Marketing email content cho KH Tiêu chuẩn | Trang + Marketing | W20 |
| B9 | Tune alerting thresholds based on safety stock | Hương + Cường + Vũ | W20 |
| B10 | Retry mechanism `gift_assignment_pending` queue | Cường | W22 |
| B11 | CRM integration API spec | Cường | W21 |
| B12 | Rollback flow KH deceased post-trigger | Cường + Trang (SOP) | W22 |

### 8.3 Open items chưa close

| # | Item | Owner | Note |
|---|---|---|---|
| O1 | Negotiation Urbox về activate-time expiry | Hương → Urbox | Confirm trước khi sign DPA |
| O2 | MB-VIP value evoucher (hỏi Marketing) | Trang | Block UC-01 sign-off final |
| O3 | Đầu mối Tri ân MBL chính thức ai? | Hương | Có thể là chính chị Hương hoặc Tri ân team |
| O4 | DWH late data — sync trễ thì batch chạy lại không? | Trang → DWH team | Chưa thảo luận trong meeting này |

---

## 9. Risks new flag

- **R13 — Budget overrun mid-year**: Forecast Bạc+Vàng+KC = 4.36 tỷ vs cap 3.5 tỷ. Q3 review có thể phải downgrade tier value, gây inconsistency nội bộ. *Mitigation*: D5 burn rate monitoring + D2 carve-out MB-VIP riêng.
- **R14 — Mapping CIF→customer_id miss rate**: Có thể 30-40% KH MB-VIP whitelist không tìm thấy match (do KH chưa đăng ký HĐBH dưới đúng CIF). *Mitigation*: D3 step 5 — flag unmatched + manual review.
- **R15 — Urbox lock-in risk**: Toàn bộ luồng phụ thuộc Urbox. Nếu Urbox raise giá / SLA giảm → MBL không có alternative kịp thời. *Mitigation*: phase 2 onboard vendor thứ 2 (Got It / VinID) làm parallel.

---

**Trang note**: Em sẽ:
1. Update BRD bản 0.3 với UC-09 + 7 decisions D1-D7.
2. Gửi minutes + action list này tới chị Thuỳ Giang (PO), anh Cave (PM), anh Duy (Designer).
3. Tổ chức follow-up review sau 2 tuần để check progress action items.

**Hương note**: Em sẽ work với Urbox về D1 + identify đầu mối Tri ân (B7) + raise budget với Finance về MB-VIP carve-out.

**Vũ note**: Anh sẽ update ADR-003 với pool model + activate-time expiry. Anh ping Cường ngày mai về schema + API endpoints.

**Cường note**: Em sẽ break tasks vào sprint planning W19 + estimate effort cho từng module.

*Meeting adjourned 11:24.*
