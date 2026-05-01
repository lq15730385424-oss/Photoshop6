# Quà sinh nhật MB Life Style — UC-01 Update + Q&A Log

**Document version**: 0.2 (draft)
**Author**: Trang (BA Lead, Squad 1 — Dịch vụ sau bán hàng)
**Date**: 2026-04-30
**Reference**:
- BRD: *Quà sinh nhật BRD.doc* (Confluence export, dated 2026-04-30)
- Requirement: *Customer care 2026_requirement_23.04.2026.xlsx* (Sheet1, R10–R16)
**Status**: PO (Thuỳ Giang) đã sign-off mục 4.1, 4.2 partial. Pending OP + Urbox + DPO.

**Changelog v0.1 → v0.2**:
- ✅ MB-VIP: chốt theo **danh sách cố định** (whitelist từ MB tập đoàn), không phụ thuộc APE.
- ✅ Kim cương: **không có ngưỡng trên** (mọi KH APE ≥300tr không nằm trong MB-VIP whitelist đều là Kim cương).
- ✅ KH Tiêu chuẩn: PO quyết định **không nhận quà evoucher** (bỏ 50K của BRD cũ).
- ✅ KH APE <10tr: vẫn gửi chúc mừng (không quà).
- ✅ KH đã mất: exclude tuyệt đối, thêm field `is_deceased` vào exclusion DWH.
- ✅ KH sinh 29/2: tổ chức ngày 28/2 năm thường.
- ➕ Thêm Section 7 — Chi tiết PII compliance với Urbox.

---

## 1. Bối cảnh thay đổi

BRD hiện tại (UC-01) chỉ định nghĩa quà sinh nhật theo 3 mức APE, không có concept "hạng khách hàng" và mặc định mọi KH ≥10tr APE đều nhận quà. Yêu cầu mới của BU (file Excel 23.04.2026) đưa khái niệm **hạng khách hàng** vào, đồng thời nâng giá trị quà cho các hạng cao và giới thiệu đối tác **Urbox** làm nguồn evoucher. Thêm vào đó, anh PM yêu cầu chuẩn hoá thành **5 hạng**, bổ sung hạng **MB-VIP** chưa được nhắc tới trong file Excel.

**Roadmap 2 giai đoạn** (theo trao đổi với anh PM):
- **Giai đoạn 1 (Q2/2026)**: Quà evoucher qua Urbox — *scope của BRD này*.
- **Giai đoạn 2 (TBD)**: Quà vật lý + theo dõi vận đơn — *scope sau, cần placeholder ngay từ giai đoạn 1 để tránh rework data model*.

---

## 2. Đề xuất update UC-01 — Business Rules

### 2.1 Bổ sung field & rule phân hạng KH

Ngoài các rule hiện có ở UC-01 (validate, anti-duplicate, update logic, exclusion), thêm **Rule 5: Phân hạng KH theo APE** vào Business Rules của UC-01.

**BR-UC01-05: Customer Tier classification by APE**

- **Source**: Yêu cầu BU 23.04.2026 + chỉ đạo PM (cần BU sign-off threshold).
- **Rule**: Mỗi KH (Bên mua bảo hiểm cá nhân với ≥1 HĐBH active) được gán 1 trong 5 hạng dựa trên **Total APE** tại thời điểm đồng bộ. Hạng được lưu thành field `customer_tier` trong bảng Customer của Customer Care Service và sync xuống các UC khác (UC-02 → UC-05).
- **Logic phân hạng (FINAL — đã sign-off bởi PO Thuỳ Giang ngày 2026-04-30, value MB-VIP chờ Marketing)**:

  | Hạng | Điều kiện | Value quà evoucher (giai đoạn 1) | Note |
  |---|---|---|---|
  | **Tiêu chuẩn** | APE < 50 triệu (bao gồm cả APE <10tr) **VÀ** KH không thuộc whitelist MB-VIP | **0đ — không nhận quà evoucher**. Chỉ chúc mừng (popup/email/zalo, **không SMS**) | PO chốt: bỏ quà 50K của BRD cũ. Marketing prepare FAQ truyền thông |
  | **Bạc** | 50tr ≤ APE < 100tr **VÀ** không thuộc whitelist MB-VIP | 150.000đ | Per Excel R15 |
  | **Vàng** | 100tr ≤ APE < 300tr **VÀ** không thuộc whitelist MB-VIP | 200.000đ | Per Excel R15 |
  | **Kim cương** | APE ≥ 300tr **VÀ** không thuộc whitelist MB-VIP | 500.000đ | **Không có ngưỡng trên** — mọi KH ≥300tr không thuộc MB-VIP đều là Kim cương |
  | **MB-VIP** | KH có `customer_id` ∈ **whitelist MB-VIP** (danh sách cố định từ MB tập đoàn) | `[Y]`đ — **Marketing chốt budget** | Whitelist override: **không phụ thuộc APE**. KH MB-VIP có APE 0đ vẫn là MB-VIP |

- **Exceptions**:
  - KH có hợp đồng đang ở trạng thái grace period: vẫn tính APE bình thường (đề xuất, chờ confirm).
  - KH có HĐ lapse trong vòng 90 ngày trước sinh nhật: chỉ tính APE của các HĐ active (không cộng HĐ lapsed).
- **Refresh frequency**: Đề xuất tính lại `customer_tier` mỗi lần job UC-01 chạy (daily). Snapshot dùng cho event sinh nhật là snapshot tại **T-1 ngày sinh nhật** (lock value để tránh case APE biến động đúng ngày sinh nhật làm tier đổi).
- **Validation logic (pseudo) — FINAL v0.2**:
  ```
  # MB-VIP whitelist override LUÔN có priority cao nhất
  IF customer_id IN mb_vip_whitelist:
      tier = "MB_VIP"
  ELIF total_active_APE < 50_000_000:           # bao gồm cả APE <10tr
      tier = "TIEU_CHUAN"
  ELIF total_active_APE < 100_000_000:
      tier = "BAC"
  ELIF total_active_APE < 300_000_000:
      tier = "VANG"
  ELSE:                                          # APE >= 300tr, không có ngưỡng trên
      tier = "KIM_CUONG"
  ```

- **Quản lý whitelist MB-VIP**:
  - Source: MB tập đoàn cung cấp danh sách (định kỳ hoặc on-demand). **Cần xác nhận với MB tập đoàn**: tần suất update (đề xuất hàng tháng), format (CSV/API), trường key (CIF MB Bank, CMND/CCCD, hay customer_id MBL).
  - Storage tại MBL: bảng `mb_vip_whitelist` trong Customer Care Service. Schema đề xuất: `customer_id` (PK), `effective_from`, `effective_to`, `source_ref` (mã MB tập đoàn), `imported_at`.
  - Mapping: nếu MB tập đoàn cung cấp CIF/CMND mà không có `customer_id` MBL, cần lookup qua DWH (key match: số CMND/CCCD).
  - Audit: log mỗi thay đổi whitelist (add/remove) để truy vết.

### 2.1bis Các business rules edge case (PO đã sign-off)

**BR-UC01-06: Loại trừ KH đã mất**
- Source: PO decision 2026-04-30 (reputation risk).
- Rule: Tuyệt đối không gửi chúc mừng/quà sinh nhật cho KH có flag `is_deceased = TRUE`. DWH bổ sung field này vào dataset sync UC-01. Logic exclusion: thêm `is_deceased = FALSE` vào điều kiện AND mục 1 BR-UC01-04 hiện có.
- Edge case bổ sung: nếu KH chuyển sang `is_deceased = TRUE` **sau** khi đã trigger gửi quà nhưng **chưa redeem**: rollback link Urbox + dừng email chuỗi sau (cần coordinate với DPO về thông báo người thân).

**BR-UC01-07: KH sinh ngày 29/2 năm nhuận**
- Source: PO decision 2026-04-30.
- Rule: Năm thường, sinh nhật được tổ chức vào **ngày 28/2**. Năm nhuận: 29/2 (đúng).
- Implementation: ở job trigger sinh nhật, check `IF birth_date.month == 2 AND birth_date.day == 29 AND NOT is_leap_year(current_year): trigger_on = "Feb 28"`.

**BR-UC01-08: KH APE < 10tr**
- Source: PO decision 2026-04-30 (no death zone in customer journey).
- Rule: KH có HĐBH active với APE < 10tr (kể cả 0đ nếu chỉ có rider không premium): vẫn nằm trong tier **Tiêu chuẩn**, vẫn nhận chúc mừng (popup/email/zalo, không SMS, không quà evoucher).

**BR-UC01-09: Snapshot APE & tier tại T-1 sinh nhật**
- Source: PO decision 2026-04-30.
- Rule: Tier áp dụng cho event sinh nhật là tier được tính tại snapshot **T-1** (1 ngày trước sinh nhật). Sau khi snapshot, tier cho event này không đổi dù APE biến động trong ngày T. Snapshot lưu vào bảng audit `customer_tier_snapshot` với key (`customer_id`, `event_date`).

### 2.2 Bổ sung field vào dataset đồng bộ từ DWH

UC-01 hiện tại đồng bộ: Customer ID, Họ tên, Ngày sinh, Giới tính, SĐT, Email, APE.
**Thêm**:
- `customer_tier` (string, enum: TIEU_CHUAN/BAC/VANG/KIM_CUONG/MB_VIP) — derived theo logic ở section 2.1, MBL compute (vì cần override whitelist).
- `is_mb_vip` (boolean) — KH có trong whitelist MB-VIP từ MB tập đoàn không.
- `is_deceased` (boolean) — KH đã mất, dùng cho exclusion BR-UC01-06.
- `address` (text, optional ở giai đoạn 1) — placeholder cho **giai đoạn 2** (quà vật lý). Đề xuất sync sẵn để tránh rework migration.
- `voucher_link` (string, nullable) — link Urbox đã được cấp cho lượt sinh nhật năm hiện tại (xem UC-07 mới).

### 2.3 Tác động đến các UC khác

| UC | Tác động |
|---|---|
| UC-02 (Email/SMS) | **Bỏ kênh SMS chúc mừng sinh nhật** (per Excel R14). Email cập nhật wording để có CTA "Nhận quà ngay" trỏ về app (per Excel R12) |
| UC-03 (Push noti) | Wording mới: *"🎉 Chúc Mừng Sinh Nhật Quý Khách 🎉 👉 Chạm để nhận quà ngay từ MB Life"* (per Excel R11). KH Tiêu chuẩn dùng wording cũ |
| UC-04 (Popup in app) | Popup dạng Certificate, click → điều hướng tới mục **Quà sinh nhật** trong **Màn Quà của tôi**. KH Tiêu chuẩn không có CTA nhận quà |
| **UC mới — UC-06: Màn Quà của tôi (Quà sinh nhật)** | **Cần bổ sung BRD**. Hiển thị: loại quà, hạn sử dụng, giá trị, ngày tặng, status (đã nhận/chưa nhận), button "Nhận quà" → deeplink Urbox |
| **UC mới — UC-07: Cấp & quản lý link Urbox** | **Cần bổ sung BRD**. OP mua bulk link → MBL gán mỗi KH 1 link unique tại thời điểm trigger sinh nhật |
| **UC mới — UC-08: Zalo OA chúc mừng + nhận quà** | Excel có wording rõ (R13). Cần bổ sung vào BRD |

---

## 3. Q&A Log với Urbox

> Tone: technical, focus integration. Trang (BA) sẽ là PIC follow up, anh Cường (IT) join meeting kỹ thuật.

### 3.1 Giai đoạn 1 — Evoucher

| # | Câu hỏi | Lý do hỏi | Người trả lời |
|---|---|---|---|
| U-01 | Mô hình cấp link evoucher: (a) bulk pre-purchase pool MBL gán dần, (b) on-demand qua API mỗi sinh nhật? | Quyết định data model + reconciliation flow. Excel R16 ngụ ý mô hình (a) | Urbox sales/tech |
| U-02 | 1 link = 1 mã evoucher 1 KH dùng (single-use), hay link generic + mã unique? | Anti-fraud, chống share link | Urbox tech |
| U-03 | TTL của evoucher kể từ ngày cấp link/code? Có config được không? | KH có thể nhận sau sinh nhật N ngày, cần biết hạn để hiển thị "Hạn sử dụng" trên màn Quà của tôi | Urbox tech |
| U-04 | Mệnh giá hỗ trợ: 150K / 200K / 500K. **MB-VIP** dự kiến 1tr (chờ BU) — Urbox có sẵn không? | Confirm catalogue evoucher | Urbox sales |
| U-05 | Format URL deep link redeem: domain, parameters, có hỗ trợ `customer_id` để track không? | Để build CTA "Nhận quà" trên app + tracking | Urbox tech |
| U-06 | API/integration spec: REST/SOAP/SFTP/portal? Auth (OAuth/API key)? Rate limit? | Estimate effort cho IT (anh Vũ — SA) | Urbox tech |
| U-07 | Webhook/callback khi KH redeem evoucher? Hay MBL phải pull báo cáo? | Cập nhật status "Đã nhận quà" trên màn Quà của tôi gần real-time | Urbox tech |
| U-08 | Báo cáo redeem rate, daily/weekly? Format? | Reconciliation với OP, tracking ROI | Urbox sales |
| U-09 | SLA uptime của hệ thống Urbox + redemption page? | NFR cho UC-06 (link click không lỗi) | Urbox tech |
| U-10 | Refund/cancel khi MBL cấp nhầm link cho sai KH? Quy trình? | Edge case: KH đổi tên, sai DOB sau sync | Urbox sales |
| U-11 | Behavior khi KH click vào link evoucher đã expired hoặc đã used? Trang lỗi của Urbox hay MBL handle? | UX của KH | Urbox tech + MBL |
| U-12 | Test environment: Urbox cung cấp sandbox hay phải test trên prod với mệnh giá nhỏ? | Plan cho QA | Urbox tech |
| U-13 | PII data: MBL có cần đẩy thông tin KH (name, phone, email) sang Urbox không hay chỉ cấp link và KH self-redeem? | Compliance — Decree 13/2023 PII protection | Urbox + MBL DPO |
| U-14 | Urbox có hỗ trợ phân nhóm catalogue theo "tier" để KH chọn quà trong giá trị mệnh giá không? Hay fix sẵn 1 voucher? | Excel hiện chưa rõ; ảnh hưởng UX trên app | Urbox sales |
| U-15 | KH redeem tại merchant có cần xuất trình app/SĐT không? Voucher physical hay digital code? | Edge case offline merchant | Urbox sales |

### 3.2 Giai đoạn 2 — Quà vật lý + tracking vận đơn

| # | Câu hỏi | Lý do hỏi | Người trả lời |
|---|---|---|---|
| U-16 | Urbox có dịch vụ quà vật lý (gift in kind) không, hay chỉ evoucher? Nếu có, catalogue theo tier? | Quyết định có dùng Urbox tiếp ở giai đoạn 2 hay tìm vendor 3PL khác | Urbox sales |
| U-17 | Carrier partner Urbox dùng (GHN/GHTK/J&T/VNPost)? Coverage toàn quốc bao gồm vùng sâu vùng xa? | Edge case: KH ở vùng remote không giao được | Urbox logistics |
| U-18 | Quy trình order quà vật lý: API hay portal? MBL push order theo batch hay real-time? | Integration design giai đoạn 2 | Urbox tech |
| U-19 | Tracking vận đơn: Urbox cung cấp tracking number ngay khi order, hay sau khi handed off cho carrier? | UX trên màn Quà của tôi (giai đoạn 2): hiển thị "Đang chuẩn bị" → "Đang giao" → "Đã giao" | Urbox tech |
| U-20 | Webhook update status vận đơn (picked up / in transit / delivered / failed)? Tần suất update? | Real-time hiển thị status; nếu polling thì plan job | Urbox tech |
| U-21 | SLA giao hàng theo zone: HN/HCM/tỉnh/remote? | NFR + truyền thông KH | Urbox logistics |
| U-22 | Behavior khi giao thất bại (KH vắng nhà, sai địa chỉ): retry mấy lần, sau đó? | Quy trình refund/redirect | Urbox logistics |
| U-23 | Chữ ký KH khi nhận hàng: mandatory không? Lưu ở Urbox hay gửi về MBL? | Audit trail | Urbox logistics |
| U-24 | Return/refund khi quà bị hỏng/sai khi nhận: KH liên hệ Urbox hay MBL? | Customer support flow | Urbox + OP |
| U-25 | Insurance vận chuyển cho quà giá trị cao (≥1tr)? | Risk management | Urbox logistics |
| U-26 | Address của KH MBL có phải đẩy sang Urbox không? Có lưu lại sau khi giao không? | PII compliance | Urbox + MBL DPO |

---

## 4. Q&A Log với BU (OP / Marketing)

> Tone: business + product. Tham gia: chị Hương, chị Huyền Trang (OP), chị Hà Trang (Digital), Marketing.

### 4.1 Phân hạng KH (chốt cho UC-01)

| # | Câu hỏi | Trạng thái |
|---|---|---|
| B-01 | Threshold APE cho từng hạng | ✅ **Chốt 2026-04-30** (PM + PO): Tiêu chuẩn <50tr, Bạc 50–<100tr, Vàng 100–<300tr, Kim cương ≥300tr (không trần), MB-VIP theo whitelist |
| B-02 | MB-VIP định nghĩa | ✅ **Chốt** — theo **danh sách cố định** từ MB tập đoàn. Whitelist override mọi APE rule |
| B-03 | Value evoucher cho **MB-VIP** | **Pending — Marketing chốt budget** (đề xuất 1.000.000đ — 2.000.000đ tuỳ ngân sách 2026) |
| B-04 | KH **Tiêu chuẩn**: 50K hay không? | ✅ **Chốt 2026-04-30** (PO Thuỳ Giang): **không nhận quà evoucher**, chỉ chúc mừng. Marketing chuẩn bị FAQ truyền thông cho KH năm trước đã nhận 50K |
| B-05 | KH có APE < 10tr | ✅ **Chốt** — vẫn gửi chúc mừng (không quà), gộp chung vào Tiêu chuẩn |
| B-05a | Số lượng KH năm 2025 đã nhận 50K (impact analysis cho B-04) | **Pending — chị Hương OP** lấy report |
| B-05b | Whitelist MB-VIP do bộ phận nào của MB tập đoàn cung cấp? Tần suất update? Format? | **Pending — chị Huyền Trang OP** liên hệ MB tập đoàn |

### 4.2 Vận hành & timing

| # | Câu hỏi | Trạng thái |
|---|---|---|
| B-06 | APE tính ở thời điểm nào | ✅ **Chốt** — snapshot **T-1 sinh nhật**, lock không đổi trong ngày T (BR-UC01-09) |
| B-07 | Refresh tier hàng ngày hay theo event | ✅ **Chốt** — daily theo job UC-01 |
| B-08 | KH đổi hạng giữa năm | ✅ **Chốt** — tier áp dụng = tier tại T-1 sinh nhật của năm đó |
| B-09 | HĐ lapse rồi reinstate trước sinh nhật | Đề xuất chỉ tính HĐ active tại T-1 — Pending OP confirm |
| B-10 | KH có HĐ doanh nghiệp + cá nhân: chỉ tính HĐ cá nhân? | BRD nói "BMBH cá nhân" → confirm chỉ HĐ cá nhân — Pending OP |
| B-11 | KH sinh ngày 29/2 | ✅ **Chốt** — tổ chức 28/2 năm thường (BR-UC01-07) |
| B-12 | KH đã mất | ✅ **Chốt** — exclude tuyệt đối, DWH bổ sung field `is_deceased` (BR-UC01-06) |
| B-12a | KH mất sau khi đã trigger gửi quà nhưng chưa redeem | **Pending DPO** — đề xuất rollback link Urbox + dừng email; cần check compliance về thông báo người thân |

### 4.3 Quy trình mua link Urbox

| # | Câu hỏi | Trạng thái |
|---|---|---|
| B-13 | Số lượng link mua trước theo quý/năm: estimate dựa trên forecast bao nhiêu KH theo tier? | Cần OP cung cấp forecast |
| B-14 | Lead time mua link Urbox: bao lâu trước batch sinh nhật phải order? | Pending Urbox SLA |
| B-15 | Budget cap quà sinh nhật / quý: nếu vượt budget thì xử lý sao (downgrade tier? cap số KH?) | **Pending — Marketing/Finance** |
| B-16 | Nếu Urbox out-of-stock evoucher mệnh giá X: fallback gì? | Pending |
| B-17 | Reconciliation: ai làm — OP, Finance, hay tự động? Tần suất? | Đề xuất OP làm tháng — Pending |
| B-18 | Audit trail cần log gì? (link cấp / KH / thời điểm cấp / status redeem) | Đề xuất full audit trail — Pending compliance |

### 4.4 UX & Customer Service

| # | Câu hỏi | Trạng thái |
|---|---|---|
| B-19 | Hạn nhận quà của KH (sau ngày sinh nhật): bao nhiêu ngày? Hết hạn thì link expire luôn hay rollback về OP? | Đề xuất 30 ngày — Pending |
| B-20 | KH phản ánh không nhận được quà / link lỗi: liên hệ kênh nào (CSKH MBL hay Urbox)? | Pending — cần định nghĩa SOP |
| B-21 | KH từ chối nhận quà (lý do tôn giáo, tang chế): có cơ chế opt-out không? | Đề xuất có flag `gift_opt_out` ở Customer — Pending |
| B-22 | Tax: quà sinh nhật ≥500K có cần khai TNCN cho KH không? | **Pending — Finance/Tax confirm** |
| B-23 | Wording email/zalo cho KH **Tiêu chuẩn** (không nhận quà): cần BU cung cấp template (Excel R13 ghi: "OP cung cấp thêm temp zalo cho KH tiêu chuẩn") | **Pending — OP** |

### 4.5 Giai đoạn 2 — Quà vật lý

| # | Câu hỏi | Trạng thái |
|---|---|---|
| B-24 | Timeline triển khai giai đoạn 2: target quý nào? | **Pending — strategic** |
| B-25 | Tier nào nhận quà vật lý? (Đề xuất: chỉ Kim cương + MB-VIP, các tier khác giữ evoucher) | Pending |
| B-26 | KH chọn quà từ catalogue hay BU fix theo tier? | Pending |
| B-27 | Address của KH lấy từ đâu: <ul><li>(a) DWH có sẵn (từ HĐBH)</li><li>(b) KH update trong app trước ngày sinh nhật</li><li>(c) Cả hai, ưu tiên KH update</li></ul> | Đề xuất (c) — Pending |
| B-28 | KH update địa chỉ trong app: cần verify (OTP/SMS) hay trust input? | Đề xuất verify nhẹ — Pending compliance |
| B-29 | KH thay đổi địa chỉ sau khi đã ship: xử lý sao? | Pending |
| B-30 | Status hiển thị trên Màn Quà của tôi (giai đoạn 2): cần BU cung cấp wording các state (vd: "Chuẩn bị quà" / "Đã giao đơn vị vận chuyển" / "Đang giao" / "Đã giao thành công" / "Giao thất bại") | **Pending — UX team + OP** |
| B-31 | Giao thất bại sau N lần: refund evoucher cho KH? Hủy luôn? Liên hệ KH manual? | Pending |
| B-32 | Compliance — quà vật lý ≥X triệu cần khai TNCN: bộ phận nào lo? | Pending |
| B-33 | Giai đoạn 2 có cần migrate KH đã nhận evoucher giai đoạn 1 sang quà vật lý không? | Pending |

---

## 5. Đề xuất next steps cho Trang (BA)

1. **Tuần này (W18/2026)**: Gửi Q&A list này cho:
   - OP (chị Hương, chị Huyền Trang) → schedule meeting 60ph để chốt mục 4.1, 4.2.
   - Marketing → confirm value MB-VIP và budget cap (mục 4.1, 4.3).
   - Anh Vũ (SA) review section 3 (Urbox tech) trước khi gửi Urbox.
2. **W19/2026**: Meeting với Urbox (cùng anh Vũ + anh Cường IT) → cover toàn bộ 3.1.
3. **W19/2026**: Update BRD bản 0.2 sau khi có B-01 → B-05 sign-off → đưa vào grooming session.
4. **W20/2026**: Lock UC-01 + UC-06 + UC-07 cho Sprint planning.
5. **Giai đoạn 2 (Q3+/2026)**: Tách BRD riêng, dùng Q&A 3.2 + 4.5 làm input.

---

## 6. Open risks (Trang flag để team biết)

- **R1 — Threshold MB-VIP chưa rõ**: Nếu BU không chốt sớm, sẽ block UC-01 → trượt sprint. *Mitigation*: dev field `customer_tier` thành config-driven, threshold lưu DB/config service để đổi không cần redeploy.
- **R2 — Mâu thuẫn BRD vs Excel cho KH Tiêu chuẩn**: Có thể gây khiếu nại từ KH cũ đang được 50K nay không nhận. *Mitigation*: Marketing chuẩn bị FAQ + truyền thông; quyết định chính thức từ Bà PO (Thuỳ Giang).
- **R3 — Privacy với Urbox (PII)**: Decree 13/2023 yêu cầu rõ purpose & consent. *Mitigation*: ký DPA với Urbox trước khi go-live; cập nhật privacy policy của MB Life Style App.
- **R4 — Giai đoạn 2 reuse data model**: Nếu giai đoạn 1 không reserve schema cho address + tracking, giai đoạn 2 sẽ migrate đau. *Mitigation*: bổ sung `address` và `voucher_metadata` (JSONB) ngay từ giai đoạn 1.
- **R5 — Urbox SLA / out-of-stock**: Phụ thuộc đối tác đơn lẻ. *Mitigation*: contract SLA + plan vendor thứ 2 cho giai đoạn 2.

---

*Trang (BA Lead) — sẵn sàng workshop làm rõ các điểm pending. Xin các anh/chị review và phản hồi trước EOD W18/2026.*

---

## 7. Chi tiết PII Compliance với Urbox

> Section này em viết theo yêu cầu chị Thuỳ Giang để chốt exposure trước khi ký DPA. Phạm vi: dữ liệu cá nhân (PII) của khách hàng MBL được chia sẻ với Urbox trong luồng quà sinh nhật giai đoạn 1 + giai đoạn 2.

### 7.1 Khung pháp lý áp dụng

| Văn bản | Nội dung quan tâm | Điều khoản chính |
|---|---|---|
| **Nghị định 13/2023/NĐ-CP** (PDPD — Personal Data Protection Decree) | Khung pháp lý cốt lõi về bảo vệ dữ liệu cá nhân tại VN, hiệu lực **01/07/2023** | Đ.3 (định nghĩa), Đ.11 (sự đồng ý), Đ.16 (quyền chủ thể), Đ.25 (xử lý qua bên thứ 3), Đ.43 (chuyển dữ liệu xuyên biên giới) |
| **Luật Bảo vệ dữ liệu cá nhân (dự thảo)** | Đang trong Quốc hội, dự kiến hiệu lực 2026 — cần monitor | Tăng mức phạt + DPO mandatory cho doanh nghiệp lớn |
| **Luật Kinh doanh Bảo hiểm 2022** | Đ.115 — bảo mật thông tin KH | Yêu cầu rõ ràng về data localization với một số loại dữ liệu BH |
| **ISO/IEC 27001 + 27701** | Standard bảo mật mà MBL/Urbox nên claim | Audit gate cho DPA |

**Vai trò các bên trong luồng Quà sinh nhật**:

- **MBL = Data Controller (Bên Kiểm soát dữ liệu cá nhân)** — quyết định "tại sao" và "như thế nào" dữ liệu KH được xử lý.
- **Urbox = Data Processor (Bên Xử lý dữ liệu cá nhân)** — xử lý dữ liệu thay mặt MBL theo hướng dẫn.
- **Carrier (giai đoạn 2)** = **Sub-processor** — ví dụ GHN/GHTK xử lý vận chuyển. Cần được liệt kê trong DPA và có thoả thuận xuôi.

### 7.2 Phân loại dữ liệu KH theo độ nhạy

| Field | Loại theo NĐ 13/2023 | Mức độ nhạy | Bắt buộc đẩy sang Urbox? |
|---|---|---|---|
| `customer_id` (mã KH MBL) | Dữ liệu cá nhân cơ bản | Thấp | **Có** (giai đoạn 1) — để Urbox map link |
| Họ tên | Dữ liệu cá nhân cơ bản | Trung bình | **Tuỳ chọn** — chỉ cần nếu Urbox cá nhân hoá nội dung evoucher |
| Số điện thoại | Dữ liệu cá nhân cơ bản | Trung bình | **Không cần** giai đoạn 1 (KH redeem qua app MBL); **cần** giai đoạn 2 cho carrier liên hệ |
| Email | Dữ liệu cá nhân cơ bản | Trung bình | **Không cần** — MBL tự gửi email |
| Ngày sinh | Dữ liệu cá nhân cơ bản | Trung bình | **Không cần** — MBL tự trigger theo DOB |
| APE / Hạng | Dữ liệu cá nhân **nhạy cảm** (tài chính, Đ.3.4 NĐ 13) | **Cao** | **Tuyệt đối không** — Urbox chỉ cần biết mệnh giá voucher (150K/200K/500K/MB-VIP), không cần biết APE thực |
| CCCD/CMND | Dữ liệu cá nhân **nhạy cảm** | **Cao** | **Không** |
| Địa chỉ giao hàng | Dữ liệu cá nhân cơ bản | Trung bình | **Cần (giai đoạn 2)** — giao quà vật lý |
| `is_deceased` | Suy luận về tình trạng sống/chết → nhạy cảm | **Cao** | **Tuyệt đối không** |
| Thông tin HĐBH | Dữ liệu y tế/tài chính (Đ.3.4 NĐ 13) | **Rất cao** | **Tuyệt đối không** |

→ **Nguyên tắc data minimization**: Trang đề xuất chỉ đẩy sang Urbox **tối thiểu**:
- **Giai đoạn 1**: `customer_id` + `voucher_face_value` (mệnh giá). Họ tên gửi sang chỉ khi Urbox bắt buộc personalize voucher.
- **Giai đoạn 2**: thêm `recipient_name`, `phone`, `address` cho carrier. **Không gửi** APE/HĐBH/giới tính/DOB.

### 7.3 Cơ sở pháp lý (legal basis) cho việc xử lý

Theo Đ.11 NĐ 13/2023, mỗi hoạt động xử lý PII cần có cơ sở pháp lý. Với luồng Quà sinh nhật:

| Hoạt động | Legal basis đề xuất | Cần làm gì |
|---|---|---|
| MBL gửi push noti / popup / email / zalo chúc mừng | **Hợp đồng** (Đ.11.1.b — thực hiện nghĩa vụ trong HĐBH "chăm sóc khách hàng") + **Lợi ích chính đáng** (Đ.11.1.f) | Cập nhật privacy notice trong HĐBH + app, làm rõ "chúc mừng sinh nhật" là một hoạt động chăm sóc KH |
| MBL chuyển `customer_id` sang Urbox để cấp evoucher | **Sự đồng ý** (Đ.11.1.a) — cụ thể, rõ ràng, opt-in | Thêm consent flow tại app: "Tôi đồng ý nhận quà sinh nhật từ đối tác MBL". Có thể bundle với T&C đăng ký app, **nhưng phải có lựa chọn opt-out riêng** |
| MBL chuyển địa chỉ KH sang Urbox + carrier (giai đoạn 2) | **Sự đồng ý** + **Hợp đồng** | Consent riêng cho mỗi lần gửi quà vật lý: "Tôi đồng ý chia sẻ địa chỉ giao hàng với đối tác giao nhận để nhận quà sinh nhật năm 2026" |

**Nguyên tắc đồng ý theo Đ.11 NĐ 13**:
- Tự nguyện
- Cụ thể (cho từng mục đích)
- Có thông tin (informed)
- Rõ ràng (express, không suy luận)
- Bằng văn bản hoặc hành động xác nhận (opt-in checkbox, không pre-tick)
- **Có thể rút lại bất cứ lúc nào** — UI phải cho phép withdrawal dễ dàng (1-tap)

### 7.4 Quyền của chủ thể dữ liệu (KH) — Đ.16 NĐ 13

KH có 11 quyền theo NĐ 13. Trang map những quyền liên quan luồng này:

| Quyền | KH có thể yêu cầu gì | MBL phải làm gì |
|---|---|---|
| Quyền được biết | Privacy notice tại nơi thu thập | Cập nhật privacy policy app + email confirmation |
| Quyền đồng ý/rút đồng ý | Bật/tắt "nhận quà sinh nhật" | UI toggle ở Settings → Privacy. Khi tắt: stop trigger, **không** rollback voucher đã cấp |
| Quyền truy cập | Xin xem dữ liệu MBL có | API/portal cho KH self-service trong 72h |
| Quyền chỉnh sửa | Cập nhật địa chỉ, SĐT | App profile cho phép edit |
| Quyền xoá | "Quên tôi" | Coordinate với DPO; xoá khỏi Customer Care DB + Urbox (trừ data legal hold theo Luật KDBH) |
| Quyền hạn chế xử lý | Tạm dừng | Flag `processing_paused` |
| Quyền phản đối | Không nhận marketing-style content | Khác với consent withdrawal — đây là phản đối active processing |
| Quyền khiếu nại | Khiếu nại lên cơ quan có thẩm quyền | SOP escalation: DPO MBL → Cục An ninh mạng (A05 Bộ CA) |

### 7.5 Yêu cầu DPA (Data Processing Agreement) với Urbox

Em đề xuất DPA tối thiểu phải có những điều khoản sau (nếu pháp chế muốn thêm thì OK):

| # | Điều khoản | Mô tả |
|---|---|---|
| DPA-01 | **Object & duration** | Mục đích xử lý (cấp evoucher / giao quà vật lý), thời hạn (theo HĐ thương mại + tối đa 90 ngày sau HĐ kết thúc cho cleanup) |
| DPA-02 | **Categories of data + data subjects** | Liệt kê chính xác fields được transfer (theo bảng 7.2) và đối tượng (KH cá nhân có HĐBH MBL active) |
| DPA-03 | **Processor obligations** | Urbox chỉ xử lý theo hướng dẫn của MBL, không dùng cho mục đích riêng (vd: marketing cross-sell sản phẩm Urbox, profiling) |
| DPA-04 | **Confidentiality** | Nhân viên Urbox tiếp xúc dữ liệu phải ký NDA + có training PII |
| DPA-05 | **Security measures** | Cụ thể: encryption in transit (TLS 1.2+) + at rest (AES-256), access control RBAC, log audit, MFA cho admin. Tham chiếu ISO 27001 |
| DPA-06 | **Sub-processors** | Urbox phải khai báo trước danh sách sub-processor (vd carrier giai đoạn 2). MBL có quyền phản đối. Mỗi sub-processor phải ký flow-down DPA |
| DPA-07 | **Cross-border transfer** | Nếu Urbox lưu data ngoài VN: phải làm hồ sơ đánh giá tác động chuyển dữ liệu xuyên biên giới (DPIA) gửi Cục An ninh mạng (Đ.43 NĐ 13) trước khi transfer. **Đề xuất ràng buộc Urbox lưu data tại VN** |
| DPA-08 | **Breach notification** | Urbox phải thông báo cho MBL trong **24 giờ** kể từ khi phát hiện sự cố. MBL phải báo cáo cơ quan trong **72 giờ** (Đ.23 NĐ 13) |
| DPA-09 | **Data subject requests** | Urbox phải hỗ trợ MBL trong việc trả lời yêu cầu của KH (truy cập, xoá, sửa) trong **5 ngày làm việc** |
| DPA-10 | **Audit rights** | MBL có quyền audit Urbox tối thiểu 1 lần/năm (hoặc khi có suspect breach), Urbox cung cấp ISO 27001 / SOC 2 report |
| DPA-11 | **Data return / deletion** | Khi kết thúc HĐ: Urbox phải xoá hoặc trả về MBL toàn bộ data trong 30 ngày, có biên bản xác nhận |
| DPA-12 | **Liability & indemnification** | Urbox chịu trách nhiệm bồi thường nếu sự cố do lỗi của Urbox. Liability cap thường là 12 tháng phí hợp đồng — pháp chế MBL deal |
| DPA-13 | **Governing law** | Luật Việt Nam, jurisdiction Toà án có thẩm quyền tại HN |

### 7.6 Data Protection Impact Assessment (DPIA)

Theo Đ.24 NĐ 13, MBL phải thực hiện **DPIA** trước khi triển khai hoạt động xử lý có rủi ro cao. Luồng quà sinh nhật:

- **Giai đoạn 1**: rủi ro **trung bình** (chỉ chuyển `customer_id`, không PII nhạy cảm). DPIA nên làm nhưng có thể nhẹ.
- **Giai đoạn 2**: rủi ro **cao** (địa chỉ + SĐT + tên + sub-processor carrier). **DPIA bắt buộc**.

DPIA report cần cover:
1. Mô tả luồng dữ liệu (có sơ đồ).
2. Cơ sở pháp lý + sự cần thiết + tỉ lệ.
3. Rủi ro cho KH (privacy, danger, financial loss).
4. Biện pháp giảm thiểu (mitigations).
5. Residual risk + acceptance.
6. Sign-off của DPO.

### 7.7 Action items cho Trang về PII

| # | Việc | Owner | Deadline |
|---|---|---|---|
| P-01 | Liaise với DPO MBL (chị X — em sẽ confirm) review section 7 này | Trang | W18/2026 |
| P-02 | Pháp chế MBL drafted DPA template, em + DPO + pháp chế Urbox align | Trang + Pháp chế | W19/2026 |
| P-03 | Cập nhật privacy policy app MB Life Style — thêm mục về Quà sinh nhật + đối tác Urbox | Marketing + Pháp chế | trước go-live |
| P-04 | Thiết kế consent flow trong app (opt-in checkbox, settings toggle, withdrawal flow) | Duy (Designer) + Trang | W19–W20/2026 |
| P-05 | DPIA giai đoạn 1 — light version | Trang + DPO | trước go-live |
| P-06 | DPIA giai đoạn 2 — full version, có sơ đồ data flow | Trang + DPO | trước kickoff giai đoạn 2 |
| P-07 | Audit log bảng `pii_transfer_log` — ghi mỗi lần đẩy data sang Urbox (timestamp, customer_id, fields, purpose) | Anh Vũ (SA) thiết kế | trong UC-07 spec |
| P-08 | Định nghĩa retention policy: data ở Urbox giữ bao lâu sau redeem? Sau expire? | Trang + DPO + Urbox | W19/2026 |

### 7.8 Risks PII flag thêm

- **R6 — Consent fatigue**: Nếu app yêu cầu quá nhiều consent (đăng ký + mỗi feature), KH bypass đại → consent invalid trên thực tế. *Mitigation*: gộp vào 1 privacy hub có toggle rõ ràng.
- **R7 — Urbox tái sử dụng data cho mục đích riêng**: Common practice trong industry. *Mitigation*: DPA-03 chặt + audit log + audit định kỳ.
- **R8 — Cross-border issue**: Nếu Urbox dùng cloud (AWS/GCP) ở Singapore, đã là cross-border. *Mitigation*: yêu cầu khai báo + push hồ sơ DPIA cross-border lên Cục An ninh mạng.
- **R9 — Phạt theo NĐ 13**: Mức phạt hành chính tối đa 5% doanh thu năm. Với quy mô MBL không nhỏ. *Mitigation*: DPO sign-off mọi DPA.

