# Meeting: Architecture Review — Quà sinh nhật
**Date**: 2026-04-30
**Time**: 14:00–15:30 (90 min)
**Attendees**: Trang (BA Lead), Vũ (Solution Architect)
**Reference docs**:
- BRD: *Quà sinh nhật BRD.doc* (v0.2 update của Trang)
- *Tài liệu thiết kế kiến trúc - Customer Platform.docx* v1.0
- *UC-01 update + Q&A Quà sinh nhật.md* (Trang draft)
**Recorder**: Trang

---

## 0. Opening

**Trang (BA)**: Anh Vũ, em vừa update BRD Quà sinh nhật bản 0.2 sau khi chốt với chị Thuỳ Giang và anh PM. Em đã đọc tài liệu kiến trúc Customer Platform v1.0 và thấy có **8 gaps** cần align trước khi vào sprint planning. Em chia agenda thành 7 mục, mỗi mục em raise issue, mong anh decide hoặc share view kỹ thuật. Đầu ra em mong là: (1) update mục lục container diagram, (2) fill bảng Integration Architecture mục 1.1 đang trống, (3) ADR cho các quyết định kiến trúc, (4) NFR cụ thể cho luồng Quà sinh nhật.

**Vũ (SA)**: OK Trang. Anh có 90 phút. Anh đề xuất cách làm: mỗi gap em mô tả problem, anh vẽ approach trên Excalidraw (anh share screen), chốt principle thay vì chốt detail. Detail anh sẽ document sau trong ADR. Build for change, không phải build cho UC-01.

---

## 1. Gap #1 — "Customer Care Service" không có trong arch doc

**Trang**: BRD UC-01 nói rõ Primary Actors là *"DWH, Customer Care Service"*, post-condition là *"Customer Care Service đồng bộ thành công dữ liệu vào DB của MB Life"*. Nhưng trong tài liệu kiến trúc Customer Platform v1.0, mục 3.3 Container diagram em đếm được 7 services: User, Eform, Account, Payment, Notification, Policy, Admin — **không có Customer Care Service**. Trong khi đó, ToC mục 3.3.5 lại ghi "Customer Service" nhưng body section 3.3.5 lại là Notification Service. Em nghĩ đây là lỗi soạn thảo, anh confirm giúp em.

**Vũ**: Em phát hiện đúng — đây là inconsistency của tài liệu, anh confirm sẽ fix. Về bản chất kiến trúc: trong v1.0 hiện tại, "thông tin khách hàng" đang **scatter** ở User Service (account/auth) và Account Service (sync data). Đó là design ban đầu cho luồng phát hành mới. Bây giờ scope mở rộng sang chăm sóc sau bán (Quà sinh nhật, kỷ niệm HĐ, CSR), anh đề xuất:

> **ADR-001**: Tách **Customer Care Service** thành service riêng (không gộp vào User Service hay Account Service).
>
> **Lý do**:
> - **Bounded context khác nhau**: User Service quản lý identity/auth (concern: login, MFA, session). Account Service quản lý data quality/sync (concern: dedupe, reconciliation). Customer Care quản lý **lifecycle quan hệ KH** (concern: tier, gift, anniversary, CSR, loyalty). Gộp = vi phạm Single Responsibility, sẽ pain khi scale.
> - **Domain ownership rõ ràng**: Squad 1 (Dịch vụ sau bán) own Customer Care. Squad khác own User/Account.
> - **Data sensitivity khác**: Customer Care chứa derived data (tier, APE snapshot). User/Account chứa identity primary data. Tách giúp audit + access control granular hơn.
>
> **Trade-off**: Thêm 1 service = thêm overhead deployment + API call. Mitigation: dùng pattern **CQRS** — Customer Care đọc snapshot từ Account Service qua Kafka event (eventual consistency OK cho use case này, không phải real-time payment).

**Trang**: OK em note. Vậy Customer Care Service own những entity nào trong scope giai đoạn 1?

**Vũ**: Ít nhất:
- `customer_tier` (snapshot daily + tại event)
- `mb_vip_whitelist`
- `gift_assignment` (KH X được gán link Urbox Y vào sinh nhật năm Z)
- `gift_redemption_status`
- `pii_transfer_log` (audit)
- `customer_care_event_log` (sinh nhật, kỷ niệm, CSR đã trigger gì)

Cộng thêm placeholder giai đoạn 2:
- `shipping_address` (KH update)
- `gift_shipment_tracking`

**Action item A1**: Vũ update tài liệu kiến trúc — fix ToC + thêm section 3.3.x Customer Care Service. Owner: Vũ. Deadline: W18.

---

## 2. Gap #2 — Có cần "Gift Service" / "Loyalty Service" riêng không?

**Trang**: BRD đã đề cập **Màn Quà của tôi** với mục Quà sinh nhật + Quà kỷ niệm HĐ. Tài liệu kiến trúc 2.4 Loyalty (mục Loyalty khách hàng) có *"Quản lý kho quà, quay quà, đổi quà"*, tức là sẽ có thêm các features khác sau (vòng quay, CSR cert đã thấy trong Excel BU). Em cần biết: gift management nằm ở đâu — Customer Care Service hay tách Gift Service riêng?

**Vũ**: Câu hỏi tốt. Anh nghiêng về **tách Gift Service / Loyalty Service riêng** với điều kiện: chỉ tách khi có ít nhất 2-3 features khác nhau. Hiện tại có 3 confirmed features: Quà sinh nhật, Quà kỷ niệm HĐ, CSR Certificate. Plus 2 features incoming theo BRD Loyalty: Quay quà, Đổi quà. → **Đủ critical mass để tách**.

> **ADR-002**: Tạo **Loyalty Service** (tên gọi chung hơn "Gift Service" vì sẽ chứa cả gamification quay thưởng).
>
> **Boundary**:
> - **Customer Care Service** own: customer_tier, MB-VIP whitelist, customer event triggers (sinh nhật, kỷ niệm) — *who deserves gift*.
> - **Loyalty Service** own: gift catalog, gift assignment, redemption, voucher pool quản lý, partner integration (Urbox, Ihealth) — *what gift, how delivered*.
> - **Notification Service** own: gửi push/email/zalo/popup template. *Không* quản lý gift.

**Trang**: Anh, vậy flow lúc trigger sinh nhật sẽ là:
1. Scheduler trigger event "birthday" cho customer X tại Customer Care Service.
2. Customer Care Service publish event `birthday_triggered` lên Kafka kèm `customer_id`, `tier`, `event_date`.
3. Loyalty Service subscribe → cấp link Urbox theo tier → publish event `gift_assigned`.
4. Notification Service subscribe → gửi push/email/popup với CTA deeplink.
Đúng không ạ?

**Vũ**: Đúng pattern, gọi là **Choreography saga** (mỗi service tự react event, không cần orchestrator trung tâm). Ưu điểm: loose coupling, dễ scale. Nhược điểm: harder to debug — em phải có distributed tracing tốt (đã có ELK-APM trong tech stack rồi). Anh cũng note: với Quà vật lý giai đoạn 2 cần saga state phức tạp hơn (compensate khi giao thất bại), lúc đó mình review lại pattern, có thể switch sang **Orchestration saga** với state machine rõ ràng.

**Action item A2**: Vũ thêm Loyalty Service vào container diagram. Sequence diagram cho flow Quà sinh nhật. Deadline: W19.

---

## 3. Gap #3 — DWH integration không có trong Integration Architecture

**Trang**: Mục 1.1 Integration Architecture trong tài liệu đang là bảng **rỗng** (chỉ có header). Mà BRD UC-01 phụ thuộc DWH cung cấp data daily. Anh giúp em fill row cho DWH integration?

**Vũ**: Đây là gap nghiêm trọng — không có integration table thì PMO không biết dependency. Anh đề xuất rows cho luồng Quà sinh nhật:

| STT | Hệ thống gọi | Hệ thống đích | Loại tích hợp | Tần suất | Mục đích | Batch / Real-time | Ghi chú |
|---|---|---|---|---|---|---|---|
| 1 | DWH (MB Ageas Group) | Customer Care Service | Kafka event hoặc S3 batch file (TBC với DWH team) | Daily | Sync customer info: id, name, DOB, gender, phone, email, total_APE, is_deceased, mb_vip_flag | **Batch** (đêm 02:00) | Format: Avro/Parquet preferred. Volume estimate ~500K records/day |
| 2 | Customer Care Service | Loyalty Service | Kafka event `birthday_triggered` | Real-time (theo job 09:00 sáng) | Trigger gift assignment | Real-time | Idempotency key: (customer_id, event_year, event_type) |
| 3 | Loyalty Service | Urbox API | REST/HTTPS | Real-time / on-demand | Cấp evoucher link cho KH | Real-time | OAuth2 client credentials. Retry với exponential backoff. SLA target P99 <2s |
| 4 | Urbox webhook | Loyalty Service | REST/HTTPS callback | Real-time event | Notify khi KH redeem evoucher | Real-time | Signed payload (HMAC). Duplicate detection by event_id |
| 5 | Loyalty Service | Notification Service | Kafka event `gift_assigned` | Real-time | Trigger gửi push/popup/email/zalo | Real-time | Carry voucher_link làm deeplink CTA |
| 6 | Notification Service | Push gateway (Firebase/APNs), Zalo OA, SMTP | REST | Real-time | Gửi message | Real-time | Existing — không impact |

**Trang**: Em note. Anh, em hỏi thêm: tại sao DWH → Customer Care anh chọn batch chứ không real-time? Quà sinh nhật ngày càng có expectation real-time.

**Vũ**: 3 lý do:
1. **DWH bản chất là analytical store**, không phải OLTP — không thiết kế để serve real-time low-latency query. Forcing real-time sẽ tốn tiền + kém ổn định.
2. **APE tính phức tạp**, đòi hỏi aggregation cross HĐBH, cross policy. DWH team có ETL pipeline daily đã chuẩn.
3. **Yêu cầu nghiệp vụ KHÔNG đòi real-time** — KH sinh nhật ngày T thì batch T-1 chạy đêm là đủ. BR-UC01-09 đã chốt snapshot tại T-1.

Nếu sau này có use case cần real-time (vd KH vừa phát hành HĐ và muốn trigger welcome ngay) thì pattern sẽ khác: Policy Service emit event direct → Customer Care subscribe. **Build for change** = giữ Customer Care subscribe Kafka, không hard-code batch only.

**Action item A3**: Trang follow-up DWH team confirm format file (Avro/Parquet/CSV?), volume actual, late-data handling. Deadline: W19.

---

## 4. Gap #4 — Urbox outbound: NFR & failure handling

**Trang**: Em đã có 15 câu Q&A với Urbox về integration. Anh muốn add gì từ góc SA?

**Vũ**: Anh add 4 NFR + failure scenarios em thêm vào danh sách hỏi Urbox:

> **NFR-Urbox-1: Latency**
> - P99 gọi API cấp link < 2s. Nếu Urbox không đáp ứng → cần discuss SLA penalty.
> - Lý do: KH click "Nhận quà" trên app, nếu chờ >3s là UX kém.
>
> **NFR-Urbox-2: Throughput**
> - Peak load: anh ước tính. Giả định MBL có ~500K KH active, 5% tier ≥Bạc = 25K KH/năm nhận quà. Phân bố sinh nhật uniform 365 ngày = ~70 KH/ngày trung bình. **NHƯNG**: peak ngày sinh nhật concentrate vào 09:00 sáng (BRD UC-03 fix giờ này). Trigger 70 events/ngày trong 1 giờ = ~1 event/phút. Không phải peak load lớn cho Urbox. Tuy nhiên ngày Tết/lễ có thể spike — em hỏi Urbox SLA tối thiểu họ commit.
>
> **NFR-Urbox-3: Availability**
> - Urbox SLA target ≥99.5% uptime (acceptable). Nếu Urbox down → Loyalty Service phải có **circuit breaker** (anh dùng Resilience4j, default trong Spring Boot stack).
> - **Graceful degradation**: nếu cấp link fail, KH vẫn nhận chúc mừng (popup/email/push), nhưng status gift = "Đang chuẩn bị quà" thay vì "Sẵn sàng nhận quà". Job retry sau 1h, 6h, 24h.
>
> **NFR-Urbox-4: Idempotency**
> - Cấp link Urbox phải idempotent với key `(customer_id, event_year)`. Nếu retry do network blip không được cấp 2 link cho 1 KH.
> - MBL gọi Urbox phải gửi `idempotency_key` (Urbox phải support) hoặc MBL self-check trước call.

**Trang**: 70 KH/ngày là số nhỏ thật, em không nghĩ tới. Còn anh, em flag thêm: **mua link Urbox** theo Excel R16 là *"OP mua trước 1 số lượng link"* — tức là pool model, không phải on-demand API. Anh chọn pattern nào?

**Vũ**: Tốt em flag. Có 2 pattern:

> **ADR-003**: Voucher provisioning pattern.
>
> **Option A — Pool model (như BU mô tả)**: OP order trước N link, nhập vào DB MBL bảng `voucher_pool`. Khi trigger sinh nhật, MBL gán 1 link từ pool cho KH.
> - Ưu: KH luôn có link sẵn, latency thấp, không phụ thuộc Urbox uptime tại moment trigger.
> - Nhược: Quản lý inventory phức tạp, OP phải forecast, có thể out-of-stock.
>
> **Option B — On-demand API**: Mỗi sinh nhật MBL call Urbox cấp link mới.
> - Ưu: Không cần inventory.
> - Nhược: Phụ thuộc Urbox availability tại moment trigger, latency cao hơn.
>
> **Anh đề xuất Option A** vì BU đã có quy trình mua trước, plus pool model decouple MBL khỏi Urbox tại thời điểm trigger. Schema:
> ```
> voucher_pool (
>   voucher_code PK,
>   redeem_url,
>   face_value,           -- 150K, 200K, 500K, ...
>   tier_eligibility,     -- BAC/VANG/KIM_CUONG/MB_VIP
>   batch_id,             -- batch OP đã mua
>   imported_at,
>   expires_at,
>   status,               -- AVAILABLE / ASSIGNED / REDEEMED / EXPIRED
>   assigned_to_customer_id,
>   assigned_at
> )
> ```
> Có index trên (face_value, status='AVAILABLE') để pop nhanh khi trigger.

**Action item A4**: Vũ design pool model schema chi tiết + reconciliation flow với Urbox. Deadline: W19.

**Action item A5**: Trang bổ sung 4 NFR Urbox + failure scenarios vào danh sách câu hỏi Urbox. Deadline: trước meeting Urbox W19.

---

## 5. Gap #5 — Birthday peak load & scheduler design

**Trang**: BRD UC-03 fix gửi push noti **9:00 sáng** ngày sinh nhật. Anh design scheduler thế nào?

**Vũ**: Đây là pattern fan-out + rate-limiting. Anh mô tả:

```
02:00  DWH ETL done → emit event customer_data_synced
02:30  Customer Care Service: compute snapshot tier T-1 cho KH có DOB == today+1
03:00  Customer Care Service: pre-create birthday_pending records (tier locked)
09:00  Cron trigger: query birthday_pending where event_date == today → emit batch event birthday_triggered
       → fan out qua Kafka topic, Loyalty Service consume parallel
       → mỗi message process: assign voucher từ pool + emit gift_assigned
       → Notification Service consume + send push
       → throttle ở Notification Service tránh spike push gateway
```

> **NFR-Birthday-Peak**:
> - Peak QPS internal: 70 events / 60 min = ~1.2 events/min average. Burst tolerable.
> - Push gateway (Firebase): rate limit ~100 req/s — quá thừa.
> - Email gateway: tuỳ provider, thường 50-100 req/s — đủ.
> - **Concern thực sự**: nếu 1 ngày toàn KH cùng tier (vd toàn Kim cương trong dịp lễ tết), pool model phải có đủ link tier đó. → Reconciliation alert khi pool < 30 days forecast.

**Trang**: Em note. Anh có suggest gì về logging?

**Vũ**: Crucial. Anh thêm:

> **Observability NFR**:
> - Log structured JSON với correlation_id xuyên các services (Customer Care → Loyalty → Notification → Urbox).
> - Metric Prometheus: `birthday_events_total`, `gift_assignment_failed_total`, `urbox_api_latency_p99`, `voucher_pool_remaining{tier}`.
> - Dashboard Grafana riêng cho luồng Quà sinh nhật.
> - Alert: pool tier X < 30 days forecast → pageDuty/email tới OP. Urbox API error rate > 5% → page tới SRE.

**Action item A6**: Vũ tạo Grafana dashboard spec + alerting rules. Deadline: W20.

---

## 6. Gap #6 — PII transfer log & audit (compliance NĐ 13/2023)

**Trang**: Section 7 trong BRD update của em (PII compliance) yêu cầu **audit log mỗi lần đẩy data sang Urbox**. Đây là requirement của Đ.16 NĐ 13 (right to access — KH có thể xin xem MBL đã chia sẻ data gì với ai). Anh design audit log thế nào?

**Vũ**: Anh đồng ý audit log là MANDATORY. Schema đề xuất:

```
pii_transfer_log (
  log_id PK (UUID),
  customer_id,
  recipient_system,        -- "URBOX", "GHN", "ZALO_OA", ...
  fields_transferred,      -- JSON array ["customer_id", "voucher_face_value"]
  legal_basis,             -- "CONSENT" / "CONTRACT" / "LEGITIMATE_INTEREST"
  consent_id,              -- FK to consent record nếu legal_basis = CONSENT
  purpose,                 -- "BIRTHDAY_GIFT_ASSIGNMENT"
  request_id,              -- correlation id
  transferred_at,
  retention_until,         -- khi nào auto-delete log này
  ip_address,              -- của caller
  status                   -- SUCCESS / FAILED
)
```

Lưu ở Customer Care Service (vì Customer Care own PII transfer policy). **Retention**: 5 năm theo standard insurance audit (consult với DPO + Pháp chế).

**Trang**: Anh, vậy nếu KH yêu cầu access (Đ.16 NĐ 13 quy định trả lời trong 72h)?

**Vũ**: Có 2 layer:
1. **Self-service query** — KH login vào app, mục Settings → Privacy → "Lịch sử chia sẻ dữ liệu" → query `pii_transfer_log` filter theo customer_id của mình. Anh đề xuất phase 2.
2. **DPO portal** — Customer Care Service expose admin API để DPO pull report khi có request từ KH gửi qua kênh CSKH. Phase 1 OK.

Cũng cần API cho **right to delete** (xoá data). Đây phức tạp hơn vì có legal hold cho insurance data (giữ 10 năm sau termination HĐBH theo Luật KDBH 2022). Anh recommend làm **soft delete + anonymization** thay vì hard delete: customer_id thay bằng hash, name thay bằng "ANONYMIZED_USER_X", giữ structural integrity của log.

**Action item A7**: Vũ design `pii_transfer_log` schema final + admin API spec cho DPO. Deadline: W20. Trang liaise với DPO confirm retention policy + delete strategy.

---

## 7. Gap #7 — Data Architecture: thiếu DB cho Customer Care + Loyalty

**Trang**: Mục 1.2 Data Architecture liệt kê 10 databases:
- admin_database, cms_database, claim_database
- happyapp_notification_database, notification_gateway_database
- payment_database, pcm_database, policy_database, refund_database, user_database

Em không thấy `customer_care_database` hay `loyalty_database`. Anh confirm thêm?

**Vũ**: Đúng, thiếu. Anh add:

> **DB-Add-1**: `customer_care_database` — own bởi Customer Care Service. Tables: customer_tier_snapshot, mb_vip_whitelist, customer_care_event_log, pii_transfer_log, customer_consent.
>
> **DB-Add-2**: `loyalty_database` — own bởi Loyalty Service. Tables: voucher_pool, gift_assignment, gift_redemption_log, partner_config (Urbox, Ihealth, ...), shipment_tracking (giai đoạn 2).
>
> **Database-per-service** principle (microservice best practice). PostgreSQL chung cluster để giảm ops cost ban đầu, tách physical sau khi quy mô đủ lớn.

Cũng cần em hỏi: **pcm_database** là gì? Anh chưa rõ — Trang check với người viết tài liệu, có thể là Policy Change Management?

**Trang**: Em sẽ check. Ý em hỏi thêm: **whitelist MB-VIP** — anh nói là "lưu trong customer_care_database" nhưng source là MB tập đoàn. Mỗi tháng cập nhật làm sao?

**Vũ**: Pattern **CDC (Change Data Capture)** lý tưởng nhưng MB tập đoàn phụ thuộc legacy systems. Anh đề xuất pragmatic:
- MB tập đoàn cung cấp **file CSV** hàng tháng qua SFTP.
- Customer Care Service có **import job** chạy 1st of month: validate format, diff với current whitelist, apply changes (add/remove), audit log từng change.
- Có versioning: bảng `mb_vip_whitelist_version` để rollback nếu file lỗi.

Khi nào MB tập đoàn ready API thì migrate. Build for change = service abstract source ra interface, đổi từ SFTP sang API không phải rewrite logic.

**Action item A8**: Vũ document data architecture additions + ADR-004 cho whitelist sync pattern. Deadline: W20.

---

## 8. Gap #8 — Security mapping: L1/L2/L3 cho Quà sinh nhật

**Trang**: Mục 4.2 Bảo mật phân cấp L1/L2/L3 cho từng control. Em không rõ luồng Quà sinh nhật áp ở mức nào?

**Vũ**: Định nghĩa MBAL Application Security Standard:
- **L1**: Public/marketing apps, ít data sensitive.
- **L2**: Customer-facing apps có PII cơ bản.
- **L3**: Apps có PII nhạy cảm (tài chính, sức khoẻ) hoặc transaction value cao.

> **ADR-005**: MB Life Style App + backend services Customer Care/Loyalty áp **L3** vì:
> - Chứa APE (financial PII nhạy cảm theo Đ.3.4 NĐ 13)
> - Chứa thông tin HĐBH (insurance)
> - Trigger transaction value (cấp evoucher 150K-1tr+)
>
> **Implications**:
> - Mật khẩu policy: ≥12 ký tự (recommended), không phải 8.
> - MFA mandatory cho admin/DPO portal.
> - Session token ≥128 bit.
> - AES-256 encryption at rest cho PII fields.
> - SSL Pinning trên app mobile.
> - Block app trên thiết bị root/jailbreak.
> - Audit log đầy đủ cho mọi PII access.
> - Penetration test trước go-live + mỗi major release.

**Trang**: Em note. Block thiết bị root/jailbreak có thể impact UX với KH dùng máy tự ROM, anh có concern?

**Vũ**: Có. Đây là trade-off security vs accessibility. Anh đề xuất **graceful warning** thay vì hard block: detect → show warning "Thiết bị của bạn có thể không an toàn, MBL không chịu trách nhiệm" + log để monitoring. Hard block chỉ khi detect malicious app cụ thể (dùng SafetyNet/DeviceCheck).

**Action item A9**: Trang ghi nhận decision này, raise với pháp chế xem có legal exposure không nếu chỉ warning.

---

## 9. Closing — Summary & Action Items

### 9.1 Kiến trúc decisions đã chốt (cần ADR formal)

| ADR | Decision | Owner |
|---|---|---|
| ADR-001 | Tách Customer Care Service riêng (không gộp User/Account) | Vũ |
| ADR-002 | Tạo Loyalty Service riêng cho gift/voucher/loyalty | Vũ |
| ADR-003 | Voucher pool model (Option A) thay vì on-demand API | Vũ |
| ADR-004 | MB-VIP whitelist sync via SFTP CSV monthly (interim, migrate API later) | Vũ |
| ADR-005 | Áp L3 security standard cho luồng Quà sinh nhật | Vũ |
| ADR-006 | Choreography saga cho luồng birthday (giai đoạn 1), review pattern khi vào giai đoạn 2 | Vũ |

### 9.2 Action items

| ID | Task | Owner | Deadline |
|---|---|---|---|
| A1 | Update tài liệu kiến trúc: fix ToC, thêm container Customer Care Service | Vũ | W18 |
| A2 | Thêm Loyalty Service + sequence diagram Quà sinh nhật | Vũ | W19 |
| A3 | Confirm DWH file format + volume + late-data handling | Trang | W19 |
| A4 | Voucher pool schema + reconciliation flow | Vũ | W19 |
| A5 | Bổ sung 4 NFR Urbox vào Q&A list | Trang | trước meeting Urbox W19 |
| A6 | Grafana dashboard + alert rules cho luồng Quà sinh nhật | Vũ | W20 |
| A7 | `pii_transfer_log` schema + DPO admin API | Vũ + Trang liaise DPO | W20 |
| A8 | Data architecture additions + ADR-004 whitelist sync | Vũ | W20 |
| A9 | Raise pháp chế về root/jailbreak warning vs block | Trang | W19 |
| A10 | (Cross-cutting) Trang gửi BRD v0.2 + meeting notes này cho team review trước grooming W19 | Trang | EOD W18 |

### 9.3 Open questions còn lại sau meeting

| # | Câu hỏi | Owner |
|---|---|---|
| O-01 | `pcm_database` là gì? Có overlap với customer_care_database không? | Trang follow-up tác giả tài liệu kiến trúc |
| O-02 | DWH có sẵn field `is_deceased` không hay phải coordinate Group team thêm? | Trang + DWH team |
| O-03 | Group MB có chính thức cung cấp whitelist MB-VIP qua SFTP/API không? | Trang + chị Huyền Trang OP |
| O-04 | Volume base actual KH active 2026 → tinh chỉnh capacity model | Trang xin từ OP |

### 9.4 Risks Vũ flag thêm

- **R10 — Kafka topic không có schema registry**: Nếu Customer Care emit event v1, v2 không backward compatible → break Loyalty/Notification consumers. *Mitigation*: deploy Confluent Schema Registry, force Avro schema versioning.
- **R11 — Pool out-of-stock**: OP forecast sai → ngày sinh nhật KH nhận "Đang chuẩn bị quà" → complaint. *Mitigation*: alert pool < 30 days, fallback policy "delay 24h, notify KH".
- **R12 — Distributed tracing chưa có**: Choreography saga debug sẽ pain nếu thiếu correlation_id end-to-end. *Mitigation*: bắt buộc correlation_id từ ngày 1, ELK-APM phải capture được.

---

**Trang note**: Em sẽ gửi minutes này cho chị Thuỳ Giang, anh PM (Cave), anh Duy (Designer) để alignment. Anh Vũ chuẩn bị ADRs trước W19 grooming session để cả team review.

**Vũ note**: Thanks Trang. Anh sẽ open epic riêng "Customer Care + Loyalty Platform foundation" để track 8 actions trên — anh ping em link sau meeting.

*Meeting adjourned 15:28.*
