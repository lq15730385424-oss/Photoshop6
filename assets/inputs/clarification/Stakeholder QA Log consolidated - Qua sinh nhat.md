# Stakeholder Q&A Log (consolidated) — Quà sinh nhật

**Doc**: BA-DEL-07
**Author**: Trang (BA Lead)
**Date**: 2026-05-04
**Version**: 1.0
**Mục đích**: Master log mọi câu hỏi/quyết định trong quá trình refine BRD. Dùng để:
- Audit trail khi có dispute "ai quyết định cái này".
- Onboard team member mới — đọc 1 file thay vì lội meeting minutes.
- Reference cho UAT/grooming khi có ambiguity.

**Convention**:
- ✅ = đã chốt
- ⏳ = đang pending
- ⚠️ = blocker

---

## Section A — Hỏi BU/PO/Marketing

### A.1 Phân hạng KH

| ID | Câu hỏi | Decision | Owner | Status |
|---|---|---|---|---|
| Q-A-001 | Threshold APE cho 5 hạng? | Tiêu chuẩn <50tr, Bạc 50-<100tr, Vàng 100-<300tr, Kim cương ≥300tr (no upper), MB-VIP whitelist | PM (Cave) + PO (Thuỳ Giang) | ✅ 2026-04-30 |
| Q-A-002 | MB-VIP định nghĩa bằng gì? | Whitelist cố định từ MB Bank quarterly, override APE rule | PM | ✅ 2026-04-30 |
| Q-A-003 | Value evoucher MB-VIP? | TBD — đề xuất 1tr-2tr | Marketing | ⚠️ Block UC-01 final |
| Q-A-004 | KH Tiêu chuẩn (BRD cũ 50K) — giữ hay bỏ? | **Bỏ** quà 50K, chỉ chúc mừng. Marketing chuẩn bị FAQ | PO | ✅ 2026-04-30 |
| Q-A-005 | KH APE <10tr | Vẫn chúc mừng (no death zone), không quà | PO | ✅ 2026-04-30 |
| Q-A-006 | Số lượng KH 2025 đã nhận 50K (impact) | ~62.500 KH, 78% là loyalty 2+ năm | OP (Hương) | ✅ 2026-05-04 |
| Q-A-007 | Whitelist MB-VIP ai cấp? | MB Bank Wealth Management, quarterly Excel email | OP (Hương) | ✅ 2026-05-04 |
| Q-A-008 | Đầu mối Tri ân MBL nhận file | TBD | Hương identify | ⏳ B7 deadline W19 |

### A.2 Edge case business

| ID | Câu hỏi | Decision | Owner | Status |
|---|---|---|---|---|
| Q-A-101 | KH chết: gửi sinh nhật? | **Exclude tuyệt đối**, DWH thêm `is_deceased` | PO | ✅ 2026-04-30 |
| Q-A-102 | KH chết post-trigger, chưa redeem? | Rollback voucher, không gửi người thân | OP (Hương) + Pháp chế | ✅ 2026-05-04 |
| Q-A-103 | KH sinh 29/2 năm thường? | Tổ chức 28/2 (industry standard) | PO | ✅ 2026-04-30 |
| Q-A-104 | KH HĐ doanh nghiệp + cá nhân: tính HĐ nào? | Chỉ HĐ cá nhân (BMBH) | BRD spec | ✅ |
| Q-A-105 | KH HĐ lapse rồi reinstate trước sinh nhật? | Chỉ tính HĐ active tại snapshot T-1 | BA proposal | ⏳ Pending OP confirm |
| Q-A-106 | KH opt-out gift: vẫn chúc mừng? | Có (BR-13). Không quà | DPO + PO | ✅ |

### A.3 Vận hành & timing

| ID | Câu hỏi | Decision | Owner | Status |
|---|---|---|---|---|
| Q-A-201 | APE tính tại thời điểm nào? | Snapshot T-1, lock không đổi ngày T (BR-02) | PO | ✅ |
| Q-A-202 | Refresh tier hàng ngày hay event-driven? | Daily theo job UC-01 02:30 | SA + PO | ✅ |
| Q-A-203 | Hạn voucher Urbox? | 6 tháng từ ngày MBL **activate code** (D1) | OP deal Urbox | ✅ 2026-05-04 |
| Q-A-204 | Lead time mua link Urbox? | 7 ngày bình thường, 14 ngày peak (Tết, 8/3, 20/10, Noel), black-out 5 ngày sát Tết | OP | ✅ 2026-05-04 |

### A.4 Ngân sách

| ID | Câu hỏi | Decision | Owner | Status |
|---|---|---|---|---|
| Q-A-301 | Budget 2026 cho Quà sinh nhật? | 3.5 tỷ (70% của 5 tỷ tổng QSN+QKN) | Finance | ✅ |
| Q-A-302 | Budget gap Bạc+Vàng+KC = 4.36 tỷ vs cap 3.5 tỷ? | Cap hard 3.5 tỷ. Q3 review burn rate, có quyền điều chỉnh tier value Q4 | OP + PO | ✅ D2 2026-05-04 |
| Q-A-303 | MB-VIP carve-out budget riêng? | YES — từ ngân sách Tri ân | OP + Marketing | ⏳ Pending Marketing confirm |
| Q-A-304 | Out-of-stock fallback? | Delay 24h + rush procurement. Không downgrade tier | OP + SA | ✅ D6 2026-05-04 |
| Q-A-305 | Tax: quà ≥500K có khai TNCN? | Không (mức ≥10tr/lần mới khai. MB-VIP max 2tr) | Finance | ✅ 2026-05-04 |

### A.5 UX & Customer Service

| ID | Câu hỏi | Decision | Owner | Status |
|---|---|---|---|---|
| Q-A-401 | Hạn KH nhận quà sau sinh nhật? | 6 tháng (từ activate, D1) | OP | ✅ |
| Q-A-402 | KH complaint không nhận được quà: liên hệ ai? | CSKH MBL → check CRM → escalate OP nếu lỗi Urbox | Hương | ✅ |
| Q-A-403 | KH từ chối nhận quà (tang chế): cơ chế? | App Settings → Privacy toggle opt-out | DPO | ✅ BR-13 |
| Q-A-404 | Wording email KH Tiêu chuẩn (UC-09 pre-birthday)? | TBD | Marketing | ⏳ B8 W20 |

---

## Section B — Hỏi Urbox

### B.1 Giai đoạn 1 — Evoucher

| ID | Câu hỏi | Decision/Answer | Owner | Status |
|---|---|---|---|---|
| Q-B-001 | Mô hình cấp link: pool hay on-demand? | **Pool model** (Option A) — OP mua trước, MBL gán dần | SA (Vũ) ADR-003 | ✅ 2026-04-30 |
| Q-B-002 | 1 link = 1 mã single-use? | Yes | Urbox | ✅ |
| Q-B-003 | TTL voucher? Config? | 6 tháng default từ ngày Urbox xuất batch. Có option activate-time clock | Hương deal | ✅ D1 |
| Q-B-004 | Mệnh giá hỗ trợ? | 150K, 200K, 500K, 1tr, 2tr — Urbox có sẵn | Hương | ✅ |
| Q-B-005 | Format URL deeplink? | Standard `https://urbox.vn/redeem/{code}?customer={id}` | Urbox tech | ⏳ TBC |
| Q-B-006 | API spec: REST/SOAP? Auth? | OAuth2 client credentials, REST | Vũ + Cường | ⏳ Meeting Urbox W19 |
| Q-B-007 | Webhook redeem? | Có. HMAC signed. | Urbox tech | ⏳ TBC |
| Q-B-008 | Báo cáo redeem rate? | Daily CSV qua email + dashboard portal | Urbox | ⏳ TBC |
| Q-B-009 | SLA uptime? | Target ≥99.5% | Urbox | ⏳ Trang request SLA contract |
| Q-B-010 | Refund/cancel sai KH? | Manual qua Urbox CS, 5 ngày | Urbox | ⏳ TBC |
| Q-B-011 | Behavior link expired/used? | Urbox page show error | Urbox | ⏳ TBC |
| Q-B-012 | Test sandbox? | Có sandbox separate | Urbox | ⏳ Trang request access |
| Q-B-013 | PII data MBL gửi tối thiểu | customer_id + face_value (không gửi name/phone/email/APE) | Trang + DPO | ✅ Per Section 7.2 BRD |
| Q-B-014 | Catalogue voucher (KH chọn)? | Urbox confirm | Urbox sales | ⏳ TBC |
| Q-B-015 | Redeem tại merchant: digital code? | Digital, scan QR hoặc nhập code | Urbox | ⏳ TBC |

### B.2 Giai đoạn 2 — Quà vật lý

(Sẽ activate khi giai đoạn 2 kickoff Q3+/2026)

| ID | Câu hỏi | Status |
|---|---|---|
| Q-B-101 | Urbox có support quà vật lý? | ⏳ Chưa hỏi |
| Q-B-102 | Carrier partner (GHN, GHTK)? | ⏳ |
| Q-B-103 | Tracking webhook? | ⏳ |
| Q-B-104 | SLA giao hàng? | ⏳ |
| Q-B-105 | Failed delivery handling? | ⏳ |
| Q-B-106 | Cross-border data (KH địa chỉ)? | ⏳ |

---

## Section C — Hỏi Tech (SA, IT)

### C.1 Architecture

| ID | Câu hỏi | Decision | Owner | Status |
|---|---|---|---|---|
| Q-C-001 | Customer Care Service tách hay gộp User/Account? | Tách riêng (ADR-001) | SA (Vũ) | ✅ 2026-04-30 |
| Q-C-002 | Gift management: service riêng? | Loyalty Service riêng (ADR-002) | SA | ✅ |
| Q-C-003 | Saga pattern? | Choreography giai đoạn 1, review giai đoạn 2 (ADR-006) | SA | ✅ |
| Q-C-004 | DWH integration pattern? | Daily batch 02:00 (Avro/Parquet TBC), Kafka event subscribe | SA | ✅ |
| Q-C-005 | DWH có sẵn `is_deceased`? | TBC | Trang follow up DWH team | ⏳ A3 W19 |
| Q-C-006 | DWH có CIF mapping field? | TBC | Trang | ⏳ B6 W19 |
| Q-C-007 | DWH late data handling? | Accept stale, dùng snapshot batch trước, log warn | SA | ✅ |
| Q-C-008 | `pcm_database` là gì? | TBC tác giả arch doc | Trang | ⏳ |

### C.2 Voucher pool implementation

| ID | Câu hỏi | Decision | Owner | Status |
|---|---|---|---|---|
| Q-C-101 | Voucher selection logic? | FIFO theo expires_at + SELECT FOR UPDATE (BR-10) | SA + IT | ✅ |
| Q-C-102 | Idempotency event birthday? | UNIQUE (customer_id, event_year, event_type) | SA | ✅ BR-09 |
| Q-C-103 | Pool upload UI: Admin Portal hay API? | Admin Portal (OP friendly) | Cường | ✅ B1 |
| Q-C-104 | Validation rules upload? | No duplicate, valid mệnh giá enum, expires_at > today+30 | Cường | ✅ |
| Q-C-105 | Safety stock policy? | Pool ≥60 days forecast per tier | OP + SA | ✅ D5 |

### C.3 Security & PII

| ID | Câu hỏi | Decision | Owner | Status |
|---|---|---|---|---|
| Q-C-201 | Security level? | L3 (financial PII sensitive per NĐ 13) | SA ADR-005 | ✅ |
| Q-C-202 | Root/jailbreak detection: block hay warn? | Warn only (graceful) | SA | ✅ A9 |
| Q-C-203 | PII transfer log retention? | 5 năm | DPO | ⏳ Pending DPO confirm |
| Q-C-204 | Right-to-delete vs legal hold 10 năm? | Soft delete + anonymize, không hard delete | SA + DPO | ✅ |
| Q-C-205 | Cross-border (Urbox AWS Singapore)? | Cần DPIA + Cục An ninh mạng notify nếu cross-border | DPO | ⏳ Pending Urbox xác nhận host region |

### C.4 NFR

| ID | Câu hỏi | Decision/Estimate | Owner | Status |
|---|---|---|---|---|
| Q-C-301 | Volume KH active 2026? | ~505K | OP | ✅ |
| Q-C-302 | Peak QPS sinh nhật 9:00? | ~70 events / 60 phút trung bình | SA estimate | ✅ |
| Q-C-303 | Tết peak load? | ~200 events/ngày | SA estimate | ✅ |
| Q-C-304 | Urbox API latency target? | P99 <2s | SA NFR | ✅ |
| Q-C-305 | Urbox API circuit breaker? | Resilience4j default Spring Boot | Vũ | ✅ |

---

## Section D — Hỏi DPO/Pháp chế

| ID | Câu hỏi | Decision | Owner | Status |
|---|---|---|---|---|
| Q-D-001 | Legal basis chuyển PII sang Urbox? | Sự đồng ý opt-in (Đ.11.1.a NĐ 13) | DPO | ✅ |
| Q-D-002 | Legal basis chúc mừng push/email? | Hợp đồng + Lợi ích chính đáng (Đ.11.1.b + .f) | DPO | ✅ |
| Q-D-003 | Consent flow trong app? | Settings toggle + opt-in onboarding, withdrawal 1-tap | DPO + Designer | ⏳ Designer P-04 |
| Q-D-004 | DPA template với Urbox? | 13 điều khoản (Section 7.5 BRD) | DPO + Pháp chế | ⏳ P-02 W19 |
| Q-D-005 | DPIA phase 1? | Light version | DPO | ⏳ P-05 |
| Q-D-006 | DPIA phase 2 (quà vật lý)? | Full DPIA mandatory | DPO | ⏳ P-06 |
| Q-D-007 | Privacy policy update? | Add Urbox + Quà sinh nhật section | Pháp chế + Marketing | ⏳ P-03 |
| Q-D-008 | Audit `pii_transfer_log` đủ chưa? | Schema OK (Section 7.5) | DPO + SA | ✅ |

---

## Section E — Hỏi Marketing

| ID | Câu hỏi | Status |
|---|---|---|
| Q-E-001 | Value voucher MB-VIP? | ⚠️ Block UC-01 sign-off final |
| Q-E-002 | Wording email pre-birthday Tiêu chuẩn UC-09? | ⏳ B8 W20 |
| Q-E-003 | FAQ truyền thông KH 50K năm 2025? | ⏳ Marketing draft |
| Q-E-004 | Confetti/animation asset cho popup? | ⏳ |
| Q-E-005 | Banner certificate design? | ⏳ Phối hợp Designer (Duy) |
| Q-E-006 | QR code download app cho footer email? | ⏳ |
| Q-E-007 | Zalo template KH Tiêu chuẩn? | ⏳ OP cung cấp R13 Excel |

---

## Statistics

| Section | Total Q | ✅ Đã chốt | ⏳ Pending | ⚠️ Blocker |
|---|---:|---:|---:|---:|
| A. BU/PO/Marketing | 26 | 16 | 9 | 1 |
| B. Urbox | 21 | 5 | 16 | 0 |
| C. Tech (SA/IT) | 24 | 17 | 7 | 0 |
| D. DPO/Pháp chế | 8 | 3 | 5 | 0 |
| E. Marketing | 7 | 0 | 6 | 1 |
| **Total** | **86** | **41** (48%) | **43** (50%) | **2** (2%) |

**2 blockers cần unblock trước UC-01 final sign-off**:
1. **Q-A-003 / Q-E-001**: Value voucher MB-VIP (Marketing).
2. *(none other tier-1 blocker tại moment này)*

---

## Update history

| Date | Updates |
|---|---|
| 2026-04-25 | Initial Q&A list (15 items với Urbox + 23 với BU) — version 0.1 |
| 2026-04-30 | Sau meeting Trang-Thuỳ Giang: chốt mục A.1 (5 hạng), A.2 (chết, 29/2). PII Section thêm |
| 2026-04-30 | Sau meeting Trang-Vũ: thêm Section C tech architecture. 8 ADRs |
| 2026-05-04 | Sau meeting 3-bên: thêm Section A.4 budget, A.5 customer service. 7 decisions D1-D7 |
| 2026-05-04 | Consolidate v1.0 — ready for grooming W19 + UAT prep W22 |
