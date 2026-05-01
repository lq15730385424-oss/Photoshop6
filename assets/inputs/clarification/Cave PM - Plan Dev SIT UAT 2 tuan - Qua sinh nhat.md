# Plan Phát triển + SIT + UAT 2 tuần — Quà sinh nhật

**Doc**: PM-PLAN-01
**Author**: Cave (PM/SM Squad 1)
**Date**: 2026-05-01 (W18 Friday)
**Plan window**: W19 Mon 2026-05-04 → W20 Fri 2026-05-15 (10 working days)
**Status**: ⚠️ Draft — cần PO + leadership sign-off Option chọn trước Mon 2026-05-04 09:00

---

## TL;DR (cho người không có thời gian)

Mình (Cave) trung thực với cả nhóm: **71 SP + 12 UAT scenarios + 8 sign-off + greenfield 2 services** **KHÔNG VỪA 2 tuần** với capacity hiện tại của Squad 1. Yes-PM ở đây = team burn out + UAT trượt + leadership mất trust khi mình phải xin extend ở day 8.

3 options đặt lên bàn:

| Option | Scope | Outcome 2 tuần | Risk | Cave recommend |
|---|---|---|---|---|
| **A — MVP-MVP** | 22 SP (3 stories happy path) | Demo-able E2E, không production | Low | ⭐ **Default chọn** |
| **B — Full MVP 4 tuần** | 71 SP đủ scope | Production-ready W22 | Medium | Pick nếu PO có deadline ngoài W20 |
| **C — Full MVP 2 tuần** | 71 SP nhồi 2 tuần | Trượt + cắt UAT corner | **High — NOT recommend** | Document để leadership thấy đã warn |

**Cần quyết định trước Mon 09:00**: bạn (user) confirm chọn option nào, ai sign-off (PO Thuỳ Giang + leadership). Sau khi chốt, mình facilitate Sprint Planning Mon 10:00.

---

## 1. Reality check — vì sao 2 tuần không vừa full scope

### 1.1 Scope đo lường được

| Artifact | Số lượng | Source |
|---|---|---|
| User stories | 12 stories, **71 SP** | `User Stories + AC - Qua sinh nhat.md` |
| UAT scenarios | 12 scenarios, ~3.5h execution | `UAT Scenarios - Qua sinh nhat.md` |
| Stakeholder sign-off | 8 bên (PO/OP/Marketing/DPO/Pháp chế/SA/QA/PM) | UAT doc section sign-off matrix |
| Services greenfield | 2 (Customer Care, Loyalty) | ADR-001, ADR-002 từ Trang-Vũ meeting |
| External integration mới | 4 (DWH batch, Urbox API, Urbox webhook, Notification) | Architecture review section 3 |
| Figma frames | 8 (5 done, 3 pending) | `Figma Status & Pending Frames.md` |
| Open questions / blockers | 22 câu (PO log) + 4 open Q (SA log) | `PO ThuyGiang - Questions to OP & BU.md` |

### 1.2 Team capacity baseline

Squad 1 capacity ước tính (từ velocity reference + sprint history giả định):

| Role | Headcount | Sprint capacity (SP) |
|---|---|---|
| Senior BE (Java/Spring) | 2 | 10 |
| Senior FE (Flutter) | 1 | 4 |
| QA | 1 | 4 |
| BA Lead (Trang) | 0.5 (shared) | 2 |
| **Tổng** | | **~20 SP / 2 tuần** |

Reference: tài liệu BA ghi *"Estimate ~3-4 sprints với team velocity ~20 SP/sprint"* — đây là baseline đã align trước.

→ **71 SP ≈ 3.5 sprints = 7 tuần**. Ép vào 2 tuần là factor **3.5x over-commit**.

### 1.3 Blockers bên ngoài chưa resolve (tới hôm nay 2026-05-01)

Block dev/SIT/UAT khởi động full scope:

| Blocker | Impact | Owner resolve | ETA |
|---|---|---|---|
| DWH file format chưa confirm (Avro/CSV?) | Block UC-01 dev | Trang follow DWH team (action A3) | W19 |
| Urbox contract chưa ký | Block UC-07 (cấp link), UC-08 redemption | OP + Pháp chế | TBC |
| MB-VIP whitelist file format MB Bank | Block MBL-301 | OP + đầu mối Tri ân (B7) | W20 |
| Voucher pool first batch chưa nhập | Block UAT-01 | OP (sau khi ký Urbox) | After W20 |
| 22 PO open questions chưa đóng | Block grooming chốt scope | Thuỳ Giang follow OP/BU | Rolling |
| Figma 3/8 frames pending (rate limit) | Block UC-06 FE dev frame Loading/Error/Dialog | Duy + upgrade plan | 24h |
| ADR-001 → ADR-006 chưa formal sign | Block dev start với confidence | Vũ | W19 |

→ Ngay cả Option A (MVP-MVP) cũng cần Trang + Vũ + OP move trong 2 ngày tới.

---

## 2. Ba Options — chi tiết

### Option A — MVP-MVP (Cave recommend) ⭐

**Mục tiêu**: 1 luồng E2E chạy được trên staging cho UAT-01 (KH Bạc happy path), demo-able cho leadership cuối W20. Không production go-live trong 2 tuần.

**Scope cắt còn 22 SP** (3 stories core):

| Story | SP | Lý do giữ |
|---|---|---|
| MBL-101 — Sync KH + classify tier | 8 | Không có data thì không có gì test |
| MBL-103 — Trigger event + assign voucher (chỉ tier Bạc, happy path) | 13 (dev đầy đủ vẫn cần) | Là core flow |
| MBL-106 — Màn Quà của tôi (chỉ AC1 + AC2) | 5 (cắt từ 8) | UI demo-able |
| **Tổng** | **~22 SP** | (vẫn over capacity 10%, nhưng acceptable buffer 0) |

**Defer khỏi 2 tuần** (ghi vào backlog Sprint 2+):

- MBL-102 snapshot tier T-1 (mock cứng tier Bạc cho UAT-01)
- MBL-104 push noti (mock manual trigger thay vì cron 09:00)
- MBL-105 Email/Zalo (defer hoàn toàn)
- MBL-107 Pre-birthday T-7 (defer)
- MBL-201/202 Voucher pool admin (mock SQL upload, no Admin Portal UI)
- MBL-301 MB-VIP whitelist (defer)
- MBL-401 CRM lookup (defer)
- MBL-402 DPO API (defer)

**UAT scope cắt** (1 scenario thay vì 12): chỉ UAT-01 happy path, sign-off bởi PO + Hương + Duy. 8 sign-off còn lại defer tới UAT round 2.

**Dev + SIT + UAT đan xen**:
- Day 1-6: Dev parallel BE + FE
- Day 5-8: SIT (overlap dev)
- Day 9: UAT-01 dry run với QA
- Day 10: UAT-01 stakeholder demo + Retro

**Definition of Done cho 2 tuần**:
- ✅ E2E flow UAT-01 chạy trên staging.mblife.vn
- ✅ pii_transfer_log có record (compliance evidence)
- ✅ 1 stakeholder demo session với 3 sign-off (PO/OP/Designer)
- ✅ Backlog Sprint 2 refined cho phần defer

---

### Option B — Full MVP 4 tuần (2 sprints)

**Mục tiêu**: Production-ready cho go-live W22, đúng scope BRD.

**Scope 71 SP chia 2 sprints**:

| Sprint | Window | Stories | SP |
|---|---|---|---|
| Sprint 1 | W19-W20 (Mon 5/4 → Fri 5/15) | MBL-101, 102, 103, 106, 201 | ~39 SP (vẫn over) |
| Sprint 2 | W21-W22 (Mon 5/18 → Fri 5/29) | MBL-104, 105, 107, 202, 301, 401, 402 | ~32 SP |

**SIT**: dồn end of Sprint 1 (W20 Thu-Fri) cho stories sprint 1, end of Sprint 2 (W22 Thu-Fri) cho phần còn lại.

**UAT**: full 12 scenarios chạy W22-W23 đúng kế hoạch BA-DEL-06.

**Pros**: Realistic, đúng scope, có buffer cho rework.
**Cons**: Push back 2 tuần so với yêu cầu hiện tại.

**Khi nào pick B**: nếu leadership có deadline cứng cho Quà sinh nhật launch (vd Tháng Hành động Phụ nữ tháng 6, hay roadmap commit quarterly), B là minimum risk.

---

### Option C — Full MVP 2 tuần (KHÔNG recommend) ❌

Để document trung thực với leadership, đây là kịch bản nếu nhồi đủ 71 SP vào 2 tuần:

**Bắt buộc phải làm để có cơ hội xảy ra**:
- Tăng team từ 4 → 8 dev (double resource) — không có pool
- Cắt unit test, cắt code review — debt khủng cho Sprint 2+
- Cắt SIT thành 1 ngày, cắt UAT thành half-day — risk regression khi go-live
- Mock toàn bộ external (DWH, Urbox, Whitelist) — nhưng không production-ready
- Skip ADR formal review — vendor lock-in / architectural debt

**Cave dự đoán outcome**: Day 7 trượt ≥30%, day 10 báo cáo phải extend, leadership trust giảm. Đây là pattern Cave đã thấy ở squad khác, mình không recommend lặp lại.

→ Document Option C để leadership có thể chọn nếu có business case cứng (vd compliance deadline). Nhưng default Cave NOT recommend.

---

## 3. Plan chi tiết Option A — Day-by-day

Giả định bạn confirm Option A ngay hôm nay (2026-05-01 Friday).

### 3.1 Pre-sprint (Cuối tuần này — Sat-Sun 5/2-5/3)

Cave (mình) làm:
- ✅ Gửi minutes này + 3 options cho PO + leadership Friday EOD
- ✅ Nếu pick A → ping team Slack: Sprint Planning Mon 09:30, prep stories #101, #103, #106
- ⏰ Sun: pull Trang + Vũ async confirm: ADR-001/002/003 final draft sẵn cho team review Mon

Trang (BA) làm:
- Confirm DWH file format trước Mon (action A3 due W19) — nếu chưa, Mon Cave escalate Group team
- Slim AC cho 3 stories chốt: chỉ giữ AC1 + AC2 happy path

Vũ (SA) làm:
- ADR-001 + ADR-002 final review-able trước Mon
- Skeleton repo Customer Care Service + Loyalty Service (Spring Boot scaffolding) deploy lên dev environment

OP (Hương) làm:
- Confirm có thể nhập 100 voucher Bạc test (sandbox Urbox) trước Wed W19

### 3.2 Sprint timeline

```
Week 1 (W19) — DEV
─────────────────────────────────────────────────────────────────
Mon 5/4   09:30 Sprint Planning (90 min)         [Cave facilitate]
          11:00 Dev kick-off + task breakdown    [Vũ tech lead]
          14:00 Daily standup tomorrow ON
          16:00 Cave 1-on-1 với Trang về DWH blocker

Tue 5/5   09:00 Standup
          BE: MBL-101 sync schema + DB migration
          FE: MBL-106 màn Quà của tôi shell + routing
          QA: SIT test plan draft
          Cave: ADR formal review session với Vũ + 2 senior BE

Wed 5/6   09:00 Standup
          BE: MBL-103 voucher assign logic
          FE: MBL-106 GiftCard component (assigned state)
          QA: SIT env setup + test data seed script
          Cave: Voucher pool first batch follow-up Hương

Thu 5/7   09:00 Standup
          BE: MBL-103 Kafka event publish + Urbox mock client
          FE: MBL-106 deeplink Urbox sandbox
          QA: SIT regression checklist
          Cave: Mid-sprint health check, risk update

Fri 5/8   09:00 Standup
          DEV CUT-OFF for Sprint 1 stories (deploy staging)
          14:00 Code review marathon (2h)
          16:00 Cave: send mid-sprint status to leadership

Week 2 (W20) — SIT + UAT
─────────────────────────────────────────────────────────────────
Mon 5/11  09:00 Standup
          QA: SIT day 1 — happy path UAT-01 dry run
          BE: bug fix from SIT findings
          Cave: schedule UAT demo Fri 14:00

Tue 5/12  09:00 Standup
          QA: SIT day 2 — error handling, idempotency
          BE: bug fix
          Cave: confirm UAT attendance: Thuỳ Giang, Hương, Duy

Wed 5/13  09:00 Standup
          QA: SIT day 3 — performance smoke + DB integrity
          BE/FE: final polish
          Cave: prep demo deck

Thu 5/14  09:00 Standup
          QA: SIT sign-off internal
          Team: UAT dry run với Cave + Trang đóng vai stakeholder
          Cave: contingency plan nếu Friday demo fail

Fri 5/15  09:00 Standup
          14:00 UAT-01 demo session (60 min) [Cave facilitate]
                - Live demo trên staging.mblife.vn
                - PO/OP/Designer sign-off form
          16:00 Sprint Review (30 min)
          16:30 Sprint Retro (45 min) [Cave facilitate]
          17:30 Cave: send sprint summary + Sprint 2 ask
```

### 3.3 RACI per workstream

| Workstream | R (Responsible) | A (Accountable) | C (Consulted) | I (Informed) |
|---|---|---|---|---|
| BE dev (MBL-101, 103) | Senior BE 1+2 | Vũ (SA) | Trang (BA), Cave | PO, Leadership |
| FE dev (MBL-106) | Senior FE Flutter | Vũ | Duy, Trang | PO |
| SIT | QA Lead | QA Lead | Vũ, BE | PO |
| UAT | PO Thuỳ Giang | PO | Cave, Hương, Duy | Leadership, Marketing, DPO |
| Voucher pool seed | Hương (OP) | Hương | Cave, Vũ | Pháp chế |
| ADR formal | Vũ | Vũ | BE team, Cave | Trang |
| Stakeholder comms | Cave | Cave | Thuỳ Giang | All |

### 3.4 Dependency checkpoints (Cave own follow-up daily)

| Checkpoint | Due | Owner | Cave action nếu trượt |
|---|---|---|---|
| DWH format confirm | Mon 5/4 EOD | Trang | Cave escalate Group DWH lead |
| Urbox sandbox API key | Tue 5/5 EOD | Hương | Cave call Urbox sales rep |
| Voucher pool 100 link Bạc | Wed 5/6 EOD | Hương | Mock data thay thế (red flag) |
| Staging environment ready | Wed 5/6 EOD | Vũ + DevOps | Cave escalate Platform team |
| Demo invite confirmed | Wed 5/13 EOD | Cave | (own action) |

### 3.5 Risk register top 5 (Cave maintain weekly)

| ID | Risk | P | I | Mitigation |
|---|---|---|---|---|
| R-001 | DWH format thay đổi → MBL-101 rework | M | H | Mock data interface từ ngày 1, abstract DWH client |
| R-002 | Urbox sandbox unstable | M | H | Dùng Wiremock nội bộ làm fallback |
| R-003 | Greenfield deploy issues (CI/CD chưa setup) | H | M | Vũ + DevOps prep Sat-Sun pre-sprint |
| R-004 | UAT-01 demo fail Fri 5/15 | L | H | Thu 5/14 dry run + contingency reschedule Mon 5/18 |
| R-005 | Team burn out (over-commit 22 SP) | M | M | Cave bảo vệ team không thêm scope mid-sprint |

### 3.6 Communication plan

| Audience | Channel | Cadence | Cave content |
|---|---|---|---|
| PO Thuỳ Giang | 1-on-1 | Mon + Wed + Fri 30 min | Burn-down, blockers, Sprint 2 prep |
| Squad team | Slack #squad1-mbl | Real-time + standup | Daily blockers, async updates |
| Leadership | Email status | Mon + Fri W19, W20 | Bi-weekly format (xem template) |
| Cross-squad SM | Sync call | Wed 16:00 | Dependencies với Squad 2 (Contact Center) — nếu có |
| OP Hương | Slack DM | Daily | Voucher pool, Urbox progress |

### 3.7 Sprint 2 ask (lock today nếu pick A)

Nếu A success Fri 5/15, mình propose Sprint 2 (W21-W22) bao gồm:
- MBL-102 snapshot T-1 (cron real)
- MBL-104 push noti production (cron 09:00)
- MBL-105 Email + Zalo
- MBL-201 Admin Portal upload (replace mock SQL)
- UAT-02 đến UAT-07 (6 scenarios còn lại P0)

Sprint 3 (W23) full UAT remaining + go-live W24.

---

## 4. Cave's asks tới các bên (decision needed)

### 4.1 Trước Mon 5/4 09:00 (3 ngày)

| Asker | Decision needed | Decision maker |
|---|---|---|
| Cave | Pick Option A / B / C | **Bạn (user) + PO Thuỳ Giang** |
| Cave | Sign-off scope cut Option A: 22 SP, defer 49 SP | PO Thuỳ Giang |
| Cave | Confirm UAT round 1 only UAT-01 (defer 11 scenarios) | PO + Hương + DPO ack |
| Cave | Approval mock DWH + Urbox cho Sprint 1 | Vũ (SA) |
| Cave | Voucher pool Sandbox Urbox first batch | Hương + Pháp chế (consent legal review) |

### 4.2 Trong Sprint 1 (rolling)

| Asker | Decision | Decision maker | Trigger |
|---|---|---|---|
| Cave | Approve "Tiêu chuẩn không quà" wording | Marketing + PO | Khi UC-04 design final |
| Cave | DPO ack scope cut 8 stakeholder → 3 cho UAT round 1 | DPO | Wed W19 |
| Cave | Allow Sprint 1 close Friday EOD with 1 story carry-over | PO | Nếu Thursday burn-down trượt |

### 4.3 Bạn (user) cụ thể cần làm gì hôm nay

1. **Confirm Cave option** A / B / C (gợi ý A)
2. **Forward plan này** cho PO Thuỳ Giang + leadership trước EOD Friday
3. **Setup meeting** Mon 09:30 Sprint Planning (Cave drafts invite nếu bạn approve)
4. **Heads-up Hương** về voucher pool first batch ask trong tuần tới

---

## 5. Cave's commitment

Nếu bạn confirm Option A hôm nay:

- ✅ Mình facilitate full Scrum events 2 tuần (Planning, Daily, Review, Retro)
- ✅ Daily blocker log + escalation cho dependency externals
- ✅ Bi-weekly status report cho leadership (sẽ kết hợp `software-project-management` skill để tạo template chuẩn)
- ✅ Bảo vệ team khỏi scope creep mid-sprint — nếu PO/leadership push thêm story, mình filter
- ✅ Trung thực với leadership Friday W19 nếu trượt — không hidden Yellow→Green

Nếu trượt mid-sprint, mình raise sớm chứ không đợi Day 10.

---

**Ký**: Cave (PM/SM Squad 1 — Dịch vụ sau bán hàng)
**Plan version**: 1.0 — chờ option sign-off
**Next update**: Mon 2026-05-04 sau Sprint Planning
