# Hệ thống Quản lý và Xác thực Văn bằng trên Blockchain (Blockchain-based Diploma Management System)

## 📌 Tổng quan dự án (Project Overview)
Đây là một giải pháp toàn diện sử dụng công nghệ Blockchain (Hyperledger Fabric) kết hợp với Mật mã học (Cryptography) mức độ sâu để lưu trữ, quản lý và xác thực tính toàn vẹn của bằng cấp giáo dục.
Điểm nhấn kỹ thuật đặc biệt nhất của dự án là việc không sử dụng các chuẩn Mật mã Đường cong Elliptic có sẵn (như secp256r1/NIST), mà hệ thống tích hợp **một chuẩn Đường cong Elliptic hoàn toàn tùy biến (Custom Elliptic Curve)** mang tên **TNM5224** (256-bit).

Hệ thống cho phép:
1. **Bộ Giáo dục (MOE)** quản lý danh sách các trường học hợp lệ.
2. **Trường học** thực hiện ký số (on-client/backend) văn bằng bằng Private Key (trên đường cong TNM5224) và gửi Hash/Chữ ký lên Blockchain.
3. **Smart Contract (Chaincode)** tự động giải mã và xác thực on-chain độ chính xác của chữ ký trước khi cấp phép lưu vào Sổ cái (Ledger).
4. **Nhà tuyển dụng / Bất kỳ ai** có thể tra cứu và xác thực văn bằng một cách minh bạch, an toàn và chống làm giả tuyệt đối.

---

## 🏛️ Kiến trúc & Công nghệ (Architecture & Tech Stack)

1. **Smart Contract / Blockchain Core (`chaincode/`)**: 
   - Viết bằng **Golang** để triển khai trên **Hyperledger Fabric**.
   - Có tích hợp gói `crypto/ecdsa` tùy chỉnh cùng bộ tham số đường cong tự định nghĩa `TNM5224` (`p, n, b, gx, gy`).
2. **Fabric Network (`organizations/`)**:
   - Cấu hình hạ tầng phân tán bằng Docker với các Orderer và Peer Nodes tiêu chuẩn của Hyperledger.
3. **Thư viện Mật mã Tùy chỉnh (Custom Cryptography)**:
   - **`go-custom-curve`**: Package Golang nền tảng cung cấp thuật toán cho Smart Contract xác thực.
   - **`LibraryCustomCurveSignature`**: Thư viện Python (`pip install`) cung cấp phương thức `generate_keypair()`, `sign()`, `verify()`, `hash_msg()` hỗ trợ các ứng dụng ngoại vi hoặc Backend tự động ký số bằng thuật toán TNM5224.
4. **Web Application (`BlockChainSignDiploma/`)**:
   - **Backend**: Python (dùng Alembic, có thể là FastAPI/Flask). Đóng vai trò cầu nối tích hợp Fabric SDK.
   - **Frontend**: Giao diện Web (NPM/NodeJS environment) cung cấp UI cho các thao tác người dùng.

---

## ⚙️ Phân tích Chi tiết Logic Chức năng (Deep-dive Logical Flow)

Hệ thống hoạt động dựa trên 3 thực thể chính: `MinistryOfEducation`, `School`, `Diploma`. Dưới đây là logic nghiệp vụ chi tiết của các chức năng trong Smart Contract:

### 1. Quản lý Thực thể (Entity Management)
*   **Khởi tạo Hệ thống (`InitLedger`)**: Tạo lập Root Authority là Bộ Giáo dục (MOE). MOE nắm giữ Public Key định danh ban đầu.
*   **Đăng ký Trường học (`CreateSchool` & `RegisterSchool`)**:
    *   `CreateSchool`: Khởi tạo một bản ghi Trường học ở trạng thái `PENDING`. Logic xử lý được thiết kế theo hướng Idempotent (gọi lại nhiều lần không sinh lỗi nếu đã tồn tại).
    *   `RegisterSchool`: Quá trình Phê duyệt. Cập nhật trạng thái từ `PENDING` sang `ACTIVE` và lưu trữ `Certificate`. Chỉ các trường `ACTIVE` mới được phép ghi văn bằng lên Blockchain.
*   **Thu hồi Quyền (`RevokeSchool`)**: Bộ GD có quyền đánh dấu `STATUS = "REVOKED"` để tước quyền cấp bằng của một trường học khi phát hiện vi phạm.

### 2. Cấp phát Văn bằng (Diploma Issuance - `IssueDiploma`)
Đây là hàm cốt lõi nhất của dự án, bao gồm 4 bước kiểm tra bảo mật chặt chẽ:
1.  **Xác thực Trạng thái Trường học**: Smart contract truy xuất DB phân tán (StateDB) để đảm bảo `schoolId` tương ứng tồn tại và có trạng thái `ACTIVE`.
2.  **Kiểm chứng Chữ ký (On-chain Verification)**: 
    *   Tham số đầu vào: `fileHash` (Hàm băm SHA-256 của văn bằng), `signature` (chuỗi hex định dạng R,S), và `schoolId`.
    *   Hàm nội bộ `verifySignatureInternal` xử lý:
        *   Tái tạo lại payload JSON gốc: `{"file_hash": "<HASH>"}`.
        *   Tiến hành băm (Hash) payload.
        *   Chuyển đổi chuỗi Hex Public Key của Trường và Chữ ký (R,S) sang kiểu `big.Int`.
        *   Thực hiện thuật toán `ecdsa.Verify` với **Đường cong Custom TNM5224** (`TNM5224()`). Chữ ký không hợp lệ bị từ chối lập tức.
3.  **Chống ghi đè (Anti-collision/Double Spend)**: Đảm bảo `fileHash` này chưa từng tồn tại trên Blockchain thông qua hàm `DiplomaExists`.
4.  **Lưu trữ vĩnh viễn**: Ghi dữ liệu Văn bằng (Thông tin SV, Mã ngành, Xếp loại) kèm trạng thái `ISSUED` vào sổ cái. Đồng thời tạo Index dạng Composite Key `school~id` (Tối ưu cho hệ cơ sở dữ liệu LevelDB) để hỗ trợ truy vấn tốc độ cao.

### 3. Tra cứu và Hủy bỏ (Query & Revocation)
*   **Hủy Bằng (`RevokeDiploma`)**: Khi phát hiện sai phạm (gian lận, in sai), hệ thống cho phép đổi trạng thái văn bằng thành `REVOKED` kèm theo `RevokeReason` (Lý do hủy). Lịch sử giao dịch là Immutable (không thể xóa bỏ hoàn toàn mà chỉ cập nhật state mới).
*   **Xác minh (`VerifyDiploma` / `GetDiplomaWithSchoolInfo`)**: Bất kỳ ai sở hữu file bằng cấp số có thể băm ra mã Hash, gửi lên hệ thống. Hệ thống sẽ trả về tính hợp lệ, trạng thái (`ISSUED`/`REVOKED`), và liên kết với thông tin của Trường cấp (`School`) và Bộ GD (`MOE`).
*   **Truy vấn Thống kê (`GetSystemStatistics` & `GetAllSchools`)**: Ứng dụng kỹ thuật `PartialCompositeKey` với prefix như `docType~id` để duyệt, phân trang và thống kê số lượng tài sản trên sổ cái một cách tối ưu mà không cần phụ thuộc vào CouchDB.

---

## 🚀 Hướng dẫn Bắt đầu (Getting Started)

1. Cài đặt các Dependencies cơ bản: Docker, Golang, Python 3.10+, Node.js.
2. Cấu hình mạng Hyperledger Fabric trong thư mục `organizations/`.
3. Build và triển khai (Deploy) Chaincode từ thư mục `chaincode/` lên Fabric Network.
4. Cài đặt Python Crypto Library phục vụ việc ký số:
   ```bash
   cd LibraryCustomCurveSignature
   pip install -e .
   ```
5. Khởi động Backend & Frontend Application trong thư mục `BlockChainSignDiploma/` cùng các file cấu hình `.env` tương ứng.