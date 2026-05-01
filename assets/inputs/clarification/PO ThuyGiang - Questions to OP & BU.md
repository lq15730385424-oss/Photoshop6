# Memo nội bộ — Câu hỏi PO ↔ OP/BU
## Quà sinh nhật MB Life Style 2026

**From**: Cán bộ trẻ Thuỳ Giang — Product Owner Squad 1 (Dịch vụ sau bán hàng)
**To**: Chị Hương, chị Huyền Trang (OP); chị Hà Trang, anh Vũ Tuấn Anh (Digital & CX); Marketing
**CC**: Em Đào (PM/SM Squad 1), em Trang (BA Lead), em Vũ (SA)
**Date**: 2026-05-01
**Re**: Xin ý kiến business 12 điểm trước khi commit Sprint goal cho Quà sinh nhật

---

Kính gửi các anh chị,

Em đã review xong BRD v2.1 + minutes 3-bên + Q&A log mà em Trang BA đã consolidate. Các điểm về **business rules** và **operations** đã được em Trang và chị Hương handle rất kỹ. Tuy nhiên với tư cách PO em vẫn cần làm rõ **12 điểm business-level** trước khi em sign-off final + commit Sprint planning W19. Mong các anh chị phản hồi trong tuần này (deadline EOD W18 — 02/05/2026).

Em xếp theo thứ tự ưu tiên: nhóm 1-3 là **blocker** cho UC-01 final sign-off; nhóm 4-12 là **important** cho release plan.

---

## 🔴 Nhóm A — Blocker cho final sign-off

### Q1. Mục tiêu kinh doanh thực sự — đo bằng metric nào?

BRD nói "tri ân khách hàng, tăng trải nghiệm". Đó là intent đẹp, nhưng:

- **KPI chính** là gì để team biết lúc nào "thắng" — retention rate? NPS? frequency app open? cross-sell conversion sau sinh nhật?
- **Baseline 2025** — KH đã nhận 50K năm 2025 có data so sánh không? Cụ thể: sau khi nhận quà 30/60/90 ngày, KH có churn ít hơn? Có pay premium đúng hạn hơn? Có open app nhiều hơn?
- **Target 2026** — em đề xuất ít nhất 3 metric với target cụ thể (vd: NPS +3 điểm trong 6 tháng, repeat app open trong 30 ngày sau sinh nhật ≥40%, chính thức complaint ≤0.5%).
- **Pivot threshold** — nếu sau Q3 metric không đạt 70% target, mình có dám pivot/scale-down không? Hay mặc định "chương trình đã chạy thì không dừng"?

> *Không có metric = chương trình rơi vào bẫy "feature factory". Em thực sự cần con số trước khi commit.*

### Q2. KH năm 2025 nhận 50K → 2026 không nhận: impact analysis có đủ không?

Chị Hương cung cấp số 62.500 KH (78% loyalty 2+ năm) và CSKH dự đoán 0.3-0.5% complaint = ~190-310 cuộc gọi. Em hỏi sâu thêm:

- **Số 0.3-0.5% là benchmark từ đâu?** (industry data? prior MBL programs?). Em lo benchmark optimistic — KH bảo hiểm long-tenure thường complaint nhiều hơn KH retail vì expectation cao hơn.
- **Segment phụ nào** trong 62.5K KH có risk complaint cao nhất? (Persona C — elderly? Persona A — traditional 35-50? KH có HĐ ≥10 năm?). Cần segment để Marketing target communication cá nhân hoá.
- **Quantitative risk**: nếu 1% complain (~625 KH) → CSKH có capacity? SLA hiện tại absorb được không?
- **Brand risk**: 1 KH complain trên Facebook MBAL fanpage → bao lâu MK detect? Crisis playbook có không?
- **Plan B** nếu pre-birthday email (UC-09) **không đủ** — có sẵn customer service script + escalation flow chưa?

> *Em không phản đối quyết định "bỏ 50K" — em cần risk plan trước khi go-live.*

### Q3. MB-VIP value voucher — Marketing chốt được chưa?

Trang BA đã flag mấy lần. Em ack đây là blocker UC-01. Em xin Marketing:

- **Số cụ thể** value/KH: 1tr? 1.5tr? 2tr?
- **Justification**: dựa vào RICE / industry benchmark (MB Private bên Bank đang tặng gì)?
- **Budget source confirm**: carve-out từ Tri ân (như chị Hương đề xuất) hay vẫn ăn vào 3.5 tỷ?
- **Differentiation play**: 350 KH MB-VIP có cần "experience" thay vì "voucher" không? (vd handwritten card, lễ tân hotline riêng, gift hampers)

> *Em prefer làm khác biệt cho 350 KH này hơn là tặng voucher cao hơn — voucher Urbox không reflect status MB-VIP.*

---

## 🟠 Nhóm B — Important cho release plan

### Q4. Customer journey — quà sinh nhật fit thế nào vào bigger picture?

- App MB Life Style đang push gì khác Q2-Q3 2026? (claim 4.0, payment auto-debit, …)
- Sinh nhật + ack (xác nhận thông tin) + claim — flow nào KH thấy trước? Có cannibalization không?
- Quà sinh nhật **có CTA dẫn về** product khác không? (vd "Nhận quà → khám phá rider mới") — em đề xuất add cross-sell hint (low-pressure) ở popup sinh nhật.

### Q5. Trade-off với 3.5 tỷ + 71 SP dev — opportunity cost gì?

- **Cùng 3.5 tỷ** đem đi đâu khác có ROI cao hơn không? (vd improve claim experience, free check-up cho KH active 5+ năm, NPS-driven feature)
- **Cùng 71 SP × 4 sprints** dev có thể làm feature gì khác? (auto-debit, claim status tracking, beneficiary management)
- Tại sao Quà sinh nhật là priority #1 cho squad 1 Q2-Q3 2026? Có analyse không?

> *Em không đề xuất bỏ feature — em cần justify cho sếp khi review roadmap.*

### Q6. Single-vendor Urbox — risk strategic không?

Anh Vũ SA đã flag R15 (vendor lock-in) và đề xuất giai đoạn 2 onboard vendor 2 (Got It / VinID). Em escalate business-level:

- **Đã evaluate Got It / VinID / Smartmate / Tnex chưa?** Nếu chưa → tại sao chọn Urbox sole-source?
- **Negotiation power**: 25K voucher/năm ở mệnh giá 150-500K = 4-12 tỷ revenue cho Urbox. Mình có **tier pricing** không? Discount theo volume?
- **Exit clause** trong contract Urbox: nếu Urbox raise giá 20% năm 2027, mình có quyền switch trong bao lâu?
- **Multi-vendor strategy**: thực ra giai đoạn 1 đã có thể onboard 2 vendors — KH chọn voucher từ catalog mở rộng, **trải nghiệm tốt hơn**. Effort thêm không lớn (em Vũ confirm). Cân nhắc?

### Q7. Brand narrative — "đồng hành bảo vệ" vs "tặng voucher mua sắm"

Em băn khoăn: voucher Urbox mua đồ ở Aeon, KFC, GS25... có **align** với brand pillar MB Life "đồng hành bảo vệ tương lai" không, hay **tự làm loãng** brand?

Alternatives em muốn discuss với Marketing:
- **Voucher dịch vụ y tế / wellness** (Ihealth, Pharmacity, gym, spa) — fit insurance theme tốt hơn
- **Voucher giáo dục / sách** (Fahasa, Tiki Trading, Edmicro) — investing in self-development
- **Donation matching** — KH choose: nhận voucher OR MBL donate tương đương sang quỹ "We build hope" (đã có CSR program R4 Excel)

> *Voucher mua sắm OK ở giai đoạn 1 vì đơn giản, nhưng năm sau cần upgrade narrative.*

### Q8. Regulator & compliance — sign-off chính thức chưa?

- **Cục Quản lý Bảo hiểm (Bộ Tài chính)** — quà tặng KH hiện hữu có thể bị xem là **"khuyến mại"** trong Luật KDBH 2022 hay không? Cần báo cáo hay register chương trình không?
- **Hội đồng quản trị MBL** — chương trình 3.5 tỷ cần quyết nghị HĐQT không, hay đã trong delegated authority của BGD?
- **Pháp chế MBL** — DPA Urbox đã ký chưa? (em biết em Trang BA đã raise nhưng status chưa update)
- **Auditor (PwC/EY/Deloitte)** — tax / accounting impact 2026 / 2027?

### Q9. Year-over-year strategy — không phải ad-hoc 2026

- **2027** budget tăng/giữ/giảm? Threshold APE có scale theo lạm phát?
- **3-year plan** quà sinh nhật evolve thế nào? (giai đoạn 1 evoucher → giai đoạn 2 quà vật lý → giai đoạn 3 personalized → … ?)
- **Sunset criteria** — nếu chương trình không drive metric, năm thứ mấy mình "kill"?

### Q10. Customer feedback loop

- **Survey** — sau khi KH redeem quà, có pop survey không? Câu hỏi gì? (NPS? satisfaction? willingness to recommend?)
- **Channel** thu thập feedback định kỳ — email survey 30 ngày sau sinh nhật?
- **Voice of Customer** — có way nào KH "đề xuất loại quà mới" không? (form trong app, email, hotline)
- **A/B test plan** — 2 wording email / 2 design popup → đo open rate, click-through?

### Q11. Edge case business — chứ không phải technical

Trang BA đã handle edge case kỹ thuật (KH chết, 29/2…). Em add edge case business:

- **Two-life policy** (vợ + chồng cùng đứng tên BMBH) — ai nhận quà? 1 quà cho cả 2, hay 2 quà riêng? (BR-14 nói chỉ tính HĐ cá nhân, nhưng 2 BMBH cùng HĐ thì sao?)
- **KH vừa phát hành HĐ trong tháng sinh nhật** (vd HĐ 03/05, sinh nhật 05/05): có nhận quà không? Risk gaming (mua HĐ chỉ để nhận quà rồi cancel cooling-off period 21 ngày).
- **KH đang complaint chưa giải quyết** — vẫn gửi quà sinh nhật? (UX awkward nếu KH đang bức xúc 1 chuyện khác).
- **KH đang dispute claim** — sensitive moment, có nên gửi quà?
- **Cooling-off period 21 ngày** — KH sinh nhật rơi vào 21 ngày của HĐ mới: họ có thể trả HĐ + giữ voucher? Cần block?

### Q12. Operations capability — đủ scale không?

- **OP team headcount hiện tại** đủ handle không?
  - 25K voucher provisioning (1.000 link bi-monthly)
  - ~190-310 complaint cuộc gọi/năm
  - Reconciliation hàng tháng với Urbox
  - MB-VIP whitelist update quarterly
- **CSKH SLA** complaint quà sinh nhật — có cần upgrade từ baseline?
- **Ticketing system** track complaint quà — đã có không, hay tích hợp vào CRM hiện tại?
- **Escalation path** khi 1 KH MB-VIP complain — direct line tới ai? (ko thể let MB Private KH wait queue như KH thông thường)

---

## 📋 Action items đề xuất

| # | Action | Owner | Deadline |
|---|---|---|---|
| 1 | Em book meeting riêng PO ↔ BU 60ph để cover Q1-Q3 (blockers) | Em (Thuỳ Giang) | EOD W18 (02/05) |
| 2 | Marketing chốt MB-VIP value + truyền thông narrative cho Q3, Q7 | Marketing | EOD W18 |
| 3 | OP cung cấp data 2025 chi tiết hơn (segment 62.5K KH, complaint data) cho Q2 | Chị Hương | W19 |
| 4 | Em present roadmap trade-off Q5 cho leadership + lấy approval | Em | W19 |
| 5 | Compliance sign-off Q8 — pháp chế + Cục Quản lý BH | Pháp chế MBL | W20 |
| 6 | Customer feedback loop Q10 — design survey + tích hợp app | Em + em Duy + em Trang | W20-21 |
| 7 | Edge case business Q11 — em rà với em Trang BA bổ sung BR mới | Em + Trang | W19 |
| 8 | OP capacity assessment Q12 — chị Hương đánh giá + escalate nếu cần thêm headcount | Chị Hương | W19 |

---

## 🤝 Em commit

Sau khi nhận phản hồi Q1-Q3 (blockers), em sẽ:
- Update **BRD v2.2** với MB-VIP value + KPI matrix.
- Lock **Sprint goal W19** với scope giảm nếu cần (em sẵn sàng cắt UC-09 pre-birthday qua sprint kế tiếp nếu Marketing chưa xong content).
- Stakeholder update bi-weekly cho leadership từ W20.
- Sprint review cuối tháng có data baseline ready để compare.

---

> *Em hiểu các anh chị bận, nhưng em phải nói "không" có chiến lược với scope hiện tại nếu thiếu các answer này — vì commit sai bây giờ sẽ tốn 4 sprint dev + 3.5 tỷ budget. Em rất appreciate nếu có buổi cà phê 30 phút với chị Hương + Marketing tuần này để align Q1-Q3.*

Em xin cảm ơn các anh chị.

Cán bộ trẻ Thuỳ Giang
Product Owner — Squad 1 Dịch vụ sau bán hàng
MB Life Insurance
