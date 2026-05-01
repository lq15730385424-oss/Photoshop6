# BRD — Tính năng Quà Sinh Nhật Evoucher (MB Life Style × Urbox)

> **Phạm vi tài liệu:** Bổ sung Use Case cho luồng nhận quà evoucher sinh nhật trên ứng dụng MB Life Style kết nối merchant Urbox.
> **Tài liệu gốc tham chiếu:** Quà sinh nhật BRD.doc (UC-01 → UC-06 hiện có)

---

## 1. Tóm tắt yêu cầu

- **Tính năng:** Thêm UC nhận quà evoucher sinh nhật trên MB Life Style app, kết nối merchant Urbox; update UC-04 (Popup)
- **Đối tượng:** BMBH cá nhân, HĐ đang inforce, tổng APE >= 50 triệu (hạng Bạc/Vàng/Kim cương/MB-VIP); KH Tiêu chuẩn giữ nguyên luồng cũ
- **Phân hạng & giá trị quà:**

| Hạng | Giá trị evoucher | Ghi chú |
|---|---|---|
| Tiêu chuẩn | Không có evoucher | Giữ nguyên luồng cũ |
| Bạc | 150.000 VND | |
| Vàng | 200.000 VND | |
| Kim cương | 500.000 VND | |
| MB-VIP | *(TBD — confirm với Hương OP BU)* | Danh sách cố định từ MB Bank gửi hàng tháng |

- **Kênh truyền thông:** Popup (updated) + Notification out/in app + Email + Zalo (bỏ SMS)
- **Loại quà:** evoucher kết nối Urbox — KH nhận qua webview Urbox trong app, xác thực SĐT + OTP

---

## 2. Danh sách UC

| UC ID | Loại | UC Name |
|---|---|---|
| UC-04 | **Update** | Popup sinh nhật có CTA Nhận quà |
| UC-07 | **New** | Hiển thị quà sinh nhật trong màn Quà của tôi |
| UC-08 | **New** | Nhận quà evoucher sinh nhật qua Urbox |
| UC-09 | **New** | Cập nhật trạng thái nhận quà từ Urbox callback |

> **Lưu ý:** UC-01 (Đồng bộ DWH) cần update thêm trường APE để phục vụ phân hạng quà — logic đồng bộ cơ bản giữ nguyên, không cần viết UC mới.

---

## 3. Use Case Chi Tiết

---

### UC-04 (Update) — Popup sinh nhật có CTA Nhận quà

#### Use Case Description

| Field | Nội dung |
|---|---|
| **Description** | Hiển thị popup chúc mừng sinh nhật cá nhân hóa khi KH đăng nhập vào app vào đúng ngày sinh nhật. Với KH hạng Bạc/Vàng/Kim cương/MB-VIP: popup có thêm button "Nhận quà" điều hướng vào mục Quà sinh nhật trong màn Quà của tôi. KH Tiêu chuẩn giữ nguyên popup cũ (chỉ có button Đóng). |
| **Primary Actors** | MB Life App (FE), Customer Care Service (BE) |
| **Pre-conditions** | - KH đăng nhập thành công vào app<br/>- Ngày hiện tại là ngày sinh nhật của KH<br/>- KH có ít nhất 1 HĐ đang inforce<br/>- Hệ thống đã xác định hạng KH (Tiêu chuẩn / Bạc / Vàng / Kim cương / MB-VIP) |
| **Post-conditions** | - Popup sinh nhật hiển thị đúng nội dung cá nhân hóa theo tên KH<br/>- KH hạng Bạc trở lên: popup có button "Nhận quà"<br/>- KH Tiêu chuẩn: popup chỉ có button "Đóng" |
| **Triggers** | KH đăng nhập thành công vào app trong ngày sinh nhật (bấm notification hoặc login bình thường) |

#### Main Flow

| Step | Actor | Mô tả |
|---|---|---|
| 1 | BE | Sau khi KH đăng nhập thành công, BE kiểm tra: ngày hiện tại = ngày sinh nhật KH |
| 2 | BE | BE đọc hạng KH từ hệ thống (Tiêu chuẩn / Bạc / Vàng / Kim cương / MB-VIP) |
| 3 | FE | FE hiển thị popup chúc mừng sinh nhật cá nhân hóa (thiệp + hiệu ứng confetti do MKT cung cấp) với nội dung: *"Chúc mừng sinh nhật Quý Khách [Tên KH]. MB Life trân quý từng khoảnh khắc đồng hành cùng Quý Khách trên hành trình bảo vệ và vun đắp hạnh phúc. Kính chúc Quý Khách một tuổi mới tràn đầy niềm vui, sức khỏe và may mắn!"* |
| 4a | FE | **Nếu KH hạng Bạc/Vàng/Kim cương/MB-VIP:** Hiển thị thêm button **"Nhận quà"** bên cạnh button "Đóng" |
| 4b | FE | **Nếu KH hạng Tiêu chuẩn:** Chỉ hiển thị button "Đóng" (giữ nguyên luồng cũ) |
| 5a | KH | KH bấm **"Nhận quà"** → Đóng popup → Điều hướng vào màn **Quà của tôi**, scroll tới mục Quà sinh nhật → UC-07 |
| 5b | KH | KH bấm **"Đóng"** → Đóng popup, trở về màn Home |

#### Alternative Flows

| # | Tình huống | Xử lý |
|---|---|---|
| AF-1 | KH chưa login / phiên hết hạn khi bấm notification | Xử lý theo luồng Login chung MBAL Style 2025, sau khi login thành công → hiển thị popup |

#### Business Rules

| # | Rule |
|---|---|
| BR-1 | Popup chỉ hiển thị **1 lần/ngày sinh nhật** — nếu KH đăng nhập nhiều lần trong ngày, popup chỉ hiện lần đầu |
| BR-2 | Tên KH lấy theo tên gắn với BP đang đăng nhập (theo rule BRD Maintain Customer) |
| BR-3 | Thiệp và hiệu ứng confetti do Marketing cung cấp |
| BR-4 | Hạng KH được đọc từ hệ thống tại thời điểm đăng nhập, không tính lại |

---

### UC-07 (New) — Hiển thị quà sinh nhật trong màn Quà của tôi

#### Use Case Description

| Field | Nội dung |
|---|---|
| **Description** | Hiển thị evoucher quà sinh nhật của KH trong danh sách Quà của tôi. Mỗi KH đủ điều kiện được hiển thị 1 item quà sinh nhật với đầy đủ thông tin giá trị, trạng thái và button hành động tương ứng. |
| **Primary Actors** | MB Life App (FE), Customer Care Service (BE) |
| **Pre-conditions** | - KH đăng nhập thành công vào app<br/>- KH có ít nhất 1 HĐ đang inforce, tổng APE >= 50 triệu<br/>- Hệ thống đã xác định hạng KH và giá trị quà tương ứng<br/>- Ngày hiện tại là ngày sinh nhật của KH (quà chỉ xuất hiện từ ngày sinh nhật) |
| **Post-conditions** | FE hiển thị đúng item quà sinh nhật với trạng thái và thông tin tương ứng |
| **Triggers** | - KH bấm "Nhận quà" trên popup sinh nhật (từ UC-04)<br/>- KH bấm notification dẫn vào màn Quà của tôi<br/>- KH tự điều hướng vào màn Quà của tôi |

#### Main Flow

| Step | Actor | Mô tả |
|---|---|---|
| 1 | FE | FE gọi BE lấy danh sách quà của KH |
| 2 | BE | BE kiểm tra KH có quà sinh nhật trong ngày không (ngày hiện tại = ngày sinh nhật + KH đủ điều kiện) |
| 3 | BE | BE trả về item quà sinh nhật kèm thông tin: loại quà, giá trị, tên chương trình, thời hạn (nếu đã có), trạng thái |
| 4 | FE | FE hiển thị item quà sinh nhật trong danh sách Quà của tôi theo đúng thiết kế Figma |
| 5 | FE | FE render trạng thái và button tương ứng theo bảng Screen Design bên dưới |

#### Screen Design

**Thông tin hiển thị trên item quà sinh nhật:**

| Field | Mô tả | Ghi chú |
|---|---|---|
| Icon quà | Icon evoucher | Theo design hệ thống |
| Giá trị quà | E-voucher trị giá [150.000 / 200.000 / 500.000] VND | Theo hạng KH |
| Tên chương trình | "Quà sinh nhật" | Fix text |
| Ngày tặng quà | Ngày sinh nhật của KH | |
| Thời hạn sử dụng | Lấy từ Urbox sau khi KH nhận quà | Hiển thị sau khi status = Đã nhận quà |
| Link quà | URL Urbox | Hiển thị sau khi status = Đã nhận quà |
| Status | Xem bảng trạng thái bên dưới | |
| Button "Hướng dẫn" | Hiển thị hướng dẫn sử dụng evoucher | Luôn hiển thị |
| Button "Nhận quà" | Kết nối Urbox → UC-08 | Chỉ hiển thị khi status = Chưa nhận quà |

**Bảng trạng thái:**

| Status | Điều kiện | Button hành động |
|---|---|---|
| **Chưa nhận quà** | KH chưa bấm "Nhận quà" hoặc chưa hoàn tất OTP bên Urbox | "Hướng dẫn" + "Nhận quà" (active) |
| **Đã nhận quà** | Urbox callback thành công (KH hoàn tất OTP) → UC-09 | "Hướng dẫn" (button "Nhận quà" ẩn) + hiển thị Link quà + Hạn sử dụng |

#### Alternative Flows

| # | Tình huống | Xử lý |
|---|---|---|
| AF-1 | KH truy cập màn Quà của tôi không phải ngày sinh nhật | Item quà sinh nhật không hiển thị trong danh sách |
| AF-2 | BE không trả được thông tin quà | Hiển thị thông báo lỗi chung, hướng dẫn thử lại |

#### Business Rules

| # | Rule |
|---|---|
| BR-1 | Mỗi KH chỉ có **1 item quà sinh nhật** duy nhất trong danh sách mỗi năm |
| BR-2 | Quà sinh nhật **chỉ hiển thị từ ngày sinh nhật** của KH (không hiển thị trước) |
| BR-3 | KH Tiêu chuẩn **không hiển thị** item quà sinh nhật trong danh sách |
| BR-4 | Nếu hạng KH thay đổi trong ngày sinh nhật → lấy hạng tại thời điểm render (IT confirm) |

---

### UC-08 (New) — Nhận quà evoucher sinh nhật qua Urbox

#### Use Case Description

| Field | Nội dung |
|---|---|
| **Description** | KH bấm button "Nhận quà" trong màn Quà của tôi → hệ thống gọi Urbox API real-time lấy unique link → lưu link → mở webview Urbox trong app → KH xác thực SĐT + OTP để nhận evoucher. Nếu KH đã được cấp link trước đó (chưa hoàn tất OTP) thì tái sử dụng link cũ, không gọi API mới. |
| **Primary Actors** | KH, MB Life App (FE), Customer Care Service (BE), Urbox (External) |
| **Pre-conditions** | - KH đăng nhập thành công<br/>- Item quà sinh nhật đang ở trạng thái "Chưa nhận quà"<br/>- KH đủ điều kiện nhận quà (hạng Bạc/Vàng/Kim cương/MB-VIP)<br/>- Kết nối internet ổn định |
| **Post-conditions** | - Webview Urbox mở thành công trong app<br/>- Link Urbox unique được lưu vào DB của MB Life<br/>- KH thực hiện xác thực SĐT + OTP trên trang Urbox |
| **Triggers** | KH bấm button **"Nhận quà"** trên item quà sinh nhật trong màn Quà của tôi |

#### Main Flow

| Step | Actor | Mô tả |
|---|---|---|
| 1 | KH | KH bấm button **"Nhận quà"** |
| 2 | BE | BE kiểm tra DB: KH đã có Urbox link được lưu chưa? |
| 3a | BE | **Nếu chưa có link:** BE gọi Urbox API với thông tin: Customer ID, hạng KH, giá trị quà → Urbox trả về unique link |
| 3b | BE | **Nếu đã có link (KH đóng webview trước đó):** Dùng lại link đã lưu, **không** gọi Urbox API mới → sang bước 5 |
| 4 | BE | BE lưu Urbox unique link vào DB gắn với Customer ID + ngày sinh nhật năm hiện tại |
| 5 | FE | FE mở **webview Urbox** trong app với link vừa lấy được |
| 6 | KH | KH nhập **số điện thoại** trên trang Urbox |
| 7 | Urbox | Urbox gửi OTP về SĐT của KH |
| 8 | KH | KH nhập OTP xác nhận |
| 9 | Urbox | Urbox xác thực OTP thành công → gửi callback về MB Life → UC-09 |

#### Alternative Flows

| # | Tình huống | Xử lý |
|---|---|---|
| AF-1 | Urbox API lỗi / timeout ở bước 3a | BE tự động retry ngầm. Nếu vượt quá số lần retry (IT & Urbox thống nhất) → FE hiển thị thông báo lỗi + hướng dẫn thử lại sau |
| AF-2 | KH đóng webview trước khi nhập SĐT hoặc trước khi hoàn tất OTP | Status giữ nguyên "Chưa nhận quà". Lần sau KH bấm "Nhận quà" → dùng lại link cũ (bước 3b) |
| AF-3 | KH nhập sai OTP | Urbox tự xử lý (hiển thị lỗi, cho phép nhập lại) — MB Life không can thiệp |
| AF-4 | Mất kết nối internet khi đang ở webview | FE hiển thị thông báo mất kết nối theo chuẩn app, KH quay lại sau |

#### Business Rules

| # | Rule |
|---|---|
| BR-1 | Mỗi KH chỉ được cấp **1 Urbox unique link** cho mỗi kỳ sinh nhật trong năm |
| BR-2 | Link đã lưu được **tái sử dụng** nếu KH chưa hoàn tất OTP — không gọi API mới |
| BR-3 | Số lần auto retry và thời gian timeout do IT thống nhất với Urbox ở bước thiết kế kỹ thuật |
| BR-4 | MB Life chỉ mở webview Urbox, **không can thiệp** vào luồng xác thực SĐT/OTP bên trong Urbox |
| BR-5 | SĐT KH nhập vào Urbox là tự điền — Urbox tự xác thực, MB Life không pre-fill hay validate |

---

### UC-09 (New) — Cập nhật trạng thái nhận quà từ Urbox callback

#### Use Case Description

| Field | Nội dung |
|---|---|
| **Description** | Sau khi KH hoàn tất xác thực OTP thành công trên trang Urbox, Urbox gửi callback (webhook) về MB Life. BE cập nhật trạng thái quà sinh nhật của KH thành "Đã nhận quà", lưu link quà và hạn sử dụng. FE phản ánh trạng thái mới khi KH quay lại màn Quà của tôi. |
| **Primary Actors** | Urbox (External), Customer Care Service (BE), MB Life App (FE) |
| **Pre-conditions** | - KH đã hoàn tất xác thực SĐT + OTP thành công trên trang Urbox<br/>- BE đã lưu Urbox unique link gắn với Customer ID (từ UC-08)<br/>- Urbox đã được cấu hình callback endpoint về MB Life |
| **Post-conditions** | - Status quà sinh nhật của KH cập nhật thành **"Đã nhận quà"**<br/>- Link quà (URL Urbox) và hạn sử dụng được lưu vào DB<br/>- FE hiển thị đúng trạng thái mới khi KH vào lại màn Quà của tôi |
| **Triggers** | Urbox gửi webhook callback về MB Life sau khi KH xác thực OTP thành công |

#### Main Flow

| Step | Actor | Mô tả |
|---|---|---|
| 1 | Urbox | Urbox gửi callback (webhook POST) về endpoint MB Life với payload: Customer ID, link quà, hạn sử dụng, timestamp xác nhận |
| 2 | BE | BE xác thực callback hợp lệ: đúng source Urbox, Customer ID tồn tại, trạng thái hiện tại = "Chưa nhận quà" |
| 3 | BE | BE cập nhật DB: status → **"Đã nhận quà"**, lưu link quà + hạn sử dụng + timestamp |
| 4 | BE | BE trả response 200 OK về Urbox xác nhận đã nhận callback |
| 5 | FE | Lần tiếp theo KH vào màn Quà của tôi: FE gọi BE → BE trả trạng thái mới → FE hiển thị: status "Đã nhận quà", link quà, hạn sử dụng; ẩn button "Nhận quà" |

#### Alternative Flows

| # | Tình huống | Xử lý |
|---|---|---|
| AF-1 | Callback Urbox đến nhưng Customer ID không tồn tại trong DB | BE trả lỗi 404, log lại để investigate, **không** cập nhật dữ liệu |
| AF-2 | Callback Urbox đến nhưng status đã là "Đã nhận quà" (duplicate callback) | BE bỏ qua, trả 200 OK để Urbox không retry, **không** ghi đè dữ liệu |
| AF-3 | BE không nhận được callback (network issue phía Urbox) | Urbox tự retry theo cơ chế webhook của Urbox. IT cần thống nhất với Urbox về retry policy |
| AF-4 | KH vẫn đang ở webview Urbox khi callback về | Status cập nhật ngầm ở BE. Khi KH quay về app và vào lại màn Quà của tôi → FE gọi lại BE → hiển thị đúng trạng thái mới |

#### Business Rules

| # | Rule |
|---|---|
| BR-1 | Callback chỉ được xử lý khi status hiện tại là **"Chưa nhận quà"** — tránh ghi đè khi có duplicate callback |
| BR-2 | BE phải **xác thực tính hợp lệ** của callback (authentication token / secret key do Urbox cung cấp) trước khi xử lý |
| BR-3 | Mọi callback nhận được phải được **log đầy đủ** (timestamp, payload, kết quả xử lý) để phục vụ audit và troubleshoot |
| BR-4 | Link quà và hạn sử dụng lưu vào DB **theo đúng dữ liệu Urbox trả về**, MB Life không tự tính hạn sử dụng |

---

## 4. Open Questions — Cần confirm với Hương (OP BU)

| # | Câu hỏi | PIC | Trạng thái |
|---|---|---|---|
| OQ-1 | KH Tiêu chuẩn: hoàn toàn không thấy mục quà sinh nhật trong Quà của tôi, hay thấy nhưng không có evoucher? | Hương (OP BU) | Chưa chốt |
| OQ-2 | MB-VIP: giá trị evoucher bao nhiêu? | Hương (OP BU) | Chưa chốt |
| OQ-3 | Ngưỡng APE phân hạng Bạc / Vàng / Kim cương cụ thể là bao nhiêu? | Hương (OP BU) | Chưa chốt |
| OQ-4 | Hạn sử dụng evoucher bao lâu kể từ ngày sinh nhật? Xử lý khi hết hạn thế nào? | Hương (OP BU) | Chưa chốt |

---

## 5. Assumptions

| # | Assumption |
|---|---|
| 1 | Hạng KH đã được tính sẵn trong hệ thống, UC chỉ đọc hạng, không tính lại |
| 2 | Urbox cung cấp API real-time trả về unique link per KH |
| 3 | Urbox cung cấp webhook/callback khi KH hoàn tất OTP thành công |
| 4 | Link Urbox còn hiệu lực đủ lâu để KH quay lại dùng |
| 5 | Số lần retry, timeout do IT thống nhất với Urbox ở bước thiết kế kỹ thuật |
| 6 | UC-01 (Đồng bộ DWH) được update thêm trường APE phục vụ phân hạng — không cần UC mới |
