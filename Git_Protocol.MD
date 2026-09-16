# Giao Thức Git Cho Dự Án Mới - Hướng Dẫn Cộng Tác Nhóm

## Mục Lục

1. [Thiết Lập Ban Đầu](#1-thiết-lập-ban-đầu)
2. [Chiến Lược Phân Nhánh](#2-chiến-lược-phân-nhánh)
3. [Quy Tắc Viết Commit Message](#3-quy-tắc-viết-commit-message)
4. [Quy Trình Làm Việc Hàng Ngày](#4-quy-trình-làm-việc-hàng-ngày)
5. [Pull Request và Code Review](#5-pull-request-và-code-review)
6. [Xử Lý Xung Đột (Merge Conflict)](#6-xử-lý-xung-đột-merge-conflict)
7. [Quy Trình Release](#7-quy-trình-release)
8. [Hotfix Khẩn Cấp](#8-hotfix-khẩn-cấp)
9. [Quy Tắc Bắt Buộc](#9-quy-tắc-bắt-buộc)

---

## 1. Thiết Lập Ban Đầu

### Cài Đặt Git

Tải và cài đặt Git từ [https://git-scm.com/downloads](https://git-scm.com/downloads), sau đó cấu hình thông tin cá nhân:

```bash
git config --global user.name "Tên Của Bạn"
git config --global user.email "email@example.com"
git config --global core.editor "code --wait"   # hoặc editor bạn dùng
git config --global init.defaultBranch main
```

### Khởi Tạo Dự Án Mới

```bash
mkdir ten-du-an
cd ten-du-an
git init
git remote add origin <url-repository>
```

### Clone Dự Án Đã Có

```bash
git clone <url-repository>
cd ten-du-an
```

### Tạo File `.gitignore`

Luôn tạo file `.gitignore` trước khi commit đầu tiên để tránh đưa file không cần thiết lên repository:

```
# Ví dụ .gitignore
node_modules/
.env
.env.local
dist/
build/
*.log
.DS_Store
```

---

## 2. Chiến Lược Phân Nhánh

Dự án áp dụng mô hình **Git Flow** với cấu trúc nhánh như sau:

```
main          (production — code ổn định, đang chạy thật)
├── develop   (staging — tích hợp các tính năng, đã test)
│   ├── feature/ten-tinh-nang    (phát triển tính năng mới)
│   ├── bugfix/mo-ta-loi         (sửa lỗi thông thường)
│   └── refactor/ten-phan        (cải tiến code)
└── hotfix/ten-loi-khan-cap      (sửa lỗi khẩn cấp trên production)
```

### Mô Tả Các Nhánh

| Nhánh | Mục đích |
|---|---|
| `main` | Code production. **Không bao giờ commit thẳng vào đây.** |
| `develop` | Nhánh tích hợp. Tất cả feature merge vào đây trước. |
| `feature/*` | Một nhánh cho mỗi tính năng mới. Tạo từ `develop`. |
| `bugfix/*` | Sửa lỗi cụ thể. Tạo từ `develop`. |
| `hotfix/*` | Sửa lỗi khẩn cấp trên production. Tạo từ `main`. |
| `release/*` | Chuẩn bị phát hành. Tạo từ `develop`. |

### Tạo Nhánh Mới

```bash
# Tạo feature branch từ develop
git checkout develop
git pull origin develop
git checkout -b feature/ten-tinh-nang

# Tạo bugfix branch
git checkout develop
git pull origin develop
git checkout -b bugfix/mo-ta-loi
```

### Quy Tắc Đặt Tên Nhánh

```
feature/login-user
feature/payment-gateway
bugfix/fix-cart-total
hotfix/security-patch-auth
release/v1.2.0
refactor/clean-api-service
```

- Dùng chữ thường, phân cách bằng dấu `-`
- Tên ngắn gọn, rõ ràng
- Không dùng ký tự đặc biệt hay dấu cách

---

## 3. Quy Tắc Viết Commit Message

### Định Dạng Chuẩn (Conventional Commits)

```
<loại>(<phạm-vi>): <mô-tả ngắn>

[nội dung chi tiết - không bắt buộc]

[footer - không bắt buộc]
```

### Các Loại Commit

| Loại | Mô tả |
|---|---|
| `feat` | Thêm tính năng mới |
| `fix` | Sửa lỗi |
| `docs` | Thay đổi tài liệu |
| `style` | Thay đổi định dạng code (không ảnh hưởng logic) |
| `refactor` | Cải tiến code, không thêm tính năng hay sửa lỗi |
| `test` | Thêm hoặc sửa test |
| `chore` | Cập nhật dependencies, cấu hình build |
| `perf` | Cải thiện hiệu năng |
| `ci` | Thay đổi cấu hình CI/CD |

### Ví Dụ Commit Message Tốt

```bash
feat(auth): thêm chức năng đăng nhập bằng Google

fix(cart): sửa lỗi tính tổng giá khi có mã giảm giá

docs(readme): cập nhật hướng dẫn cài đặt

refactor(api): tái cấu trúc service gọi API người dùng
```

### Quy Tắc Commit

- Dòng tiêu đề **tối đa 72 ký tự**
- Dùng thì **hiện tại** ("thêm tính năng" không phải "đã thêm tính năng")
- Mỗi commit chỉ làm **một việc duy nhất**
- Commit thường xuyên, không để dồn quá nhiều thay đổi

---

## 4. Quy Trình Làm Việc Hàng Ngày

### Bước 1: Cập Nhật Code Mới Nhất

```bash
git checkout develop
git pull origin develop
```

### Bước 2: Tạo Nhánh Làm Việc

```bash
git checkout -b feature/ten-tinh-nang-cua-ban
```

### Bước 3: Phát Triển và Commit

```bash
# Xem trạng thái các file thay đổi
git status

# Thêm file vào staging (chọn lọc, không dùng git add . bừa bãi)
git add src/components/LoginForm.tsx
git add src/services/authService.ts

# Hoặc thêm tất cả thay đổi trong thư mục hiện tại
git add .

# Commit với message rõ ràng
git commit -m "feat(auth): thêm form đăng nhập với validation"
```

### Bước 4: Đẩy Nhánh Lên Remote

```bash
git push origin feature/ten-tinh-nang-cua-ban
```

### Bước 5: Giữ Nhánh Đồng Bộ Với Develop

Trong quá trình làm việc, thường xuyên cập nhật nhánh của bạn với `develop` để tránh xung đột lớn:

```bash
git fetch origin
git rebase origin/develop
# hoặc
git merge origin/develop
```

---

## 5. Pull Request và Code Review

### Tạo Pull Request (PR)

Sau khi hoàn thành tính năng, tạo PR từ nhánh của bạn vào `develop`:

1. Lên GitHub/GitLab, tạo Pull Request mới
2. **Tiêu đề PR**: rõ ràng, mô tả đúng thay đổi (tối đa 70 ký tự)
3. **Mô tả PR** phải bao gồm:
   - Tóm tắt những thay đổi đã làm
   - Lý do thay đổi (nếu cần)
   - Cách test/kiểm tra
   - Screenshot (nếu có thay đổi UI)
   - Các vấn đề đã biết hoặc chưa giải quyết

### Template Mô Tả PR

```markdown
## Tóm Tắt Thay Đổi
Mô tả ngắn gọn những gì đã thay đổi và tại sao.

## Loại Thay Đổi
- [ ] Tính năng mới (feat)
- [ ] Sửa lỗi (fix)
- [ ] Cải tiến code (refactor)
- [ ] Tài liệu (docs)

## Cách Test
1. Bước 1...
2. Bước 2...

## Checklist
- [ ] Code đã được review lại bởi chính mình
- [ ] Đã viết/cập nhật test
- [ ] Không có lỗi lint
- [ ] Tài liệu đã cập nhật (nếu cần)
```

### Quy Tắc Review Code

**Người review phải:**
- Review trong vòng **24 giờ** kể từ khi được assign
- Kiểm tra logic, hiệu năng, bảo mật
- Để lại comment cụ thể, mang tính xây dựng
- Approve khi code đạt yêu cầu

**Người được review phải:**
- Không merge khi chưa có ít nhất **1 approval**
- Phản hồi tất cả comment trước khi merge
- Không tự approve PR của chính mình

---

## 6. Xử Lý Xung Đột (Merge Conflict)

### Khi Xảy Ra Xung Đột

```bash
# Cập nhật nhánh gốc
git fetch origin
git rebase origin/develop

# Git sẽ báo file có xung đột, mở file đó và chỉnh sửa
# Phần xung đột trông như sau:
# <<<<<<< HEAD (thay đổi của bạn)
# code của bạn
# =======
# code từ develop
# >>>>>>> origin/develop

# Sau khi giải quyết xong, tiếp tục rebase
git add <file-da-sua>
git rebase --continue
```

### Nguyên Tắc Giải Quyết Xung Đột

- **Trao đổi** với người viết code kia trước khi tự quyết định
- Không xóa code của người khác khi không chắc
- Test kỹ sau khi giải quyết xung đột
- Commit riêng cho phần giải quyết xung đột nếu cần

---

## 7. Quy Trình Release

### Tạo Release Branch

```bash
# Từ develop, tạo release branch
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0
```

### Chuẩn Bị Release

```bash
# Cập nhật version trong package.json, CHANGELOG, v.v.
# Chỉ fix bug nhỏ trong release branch, không thêm tính năng mới

git commit -m "chore(release): chuẩn bị phiên bản v1.2.0"
```

### Merge Release

```bash
# Merge vào main
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags

# Merge ngược lại develop để đồng bộ
git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop

# Xóa release branch
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

---

## 8. Hotfix Khẩn Cấp

Khi có lỗi nghiêm trọng trên production cần sửa ngay:

```bash
# Tạo hotfix từ main
git checkout main
git pull origin main
git checkout -b hotfix/ten-loi-can-sua

# Sửa lỗi, commit
git commit -m "fix(auth): vá lỗ hổng bảo mật xác thực token"

# Merge vào main
git checkout main
git merge --no-ff hotfix/ten-loi-can-sua
git tag -a v1.1.1 -m "Hotfix v1.1.1"
git push origin main --tags

# Merge vào develop để đồng bộ
git checkout develop
git merge --no-ff hotfix/ten-loi-can-sua
git push origin develop

# Xóa hotfix branch
git branch -d hotfix/ten-loi-can-sua
git push origin --delete hotfix/ten-loi-can-sua
```

---

## 9. Quy Tắc Bắt Buộc

### Tuyệt Đối Không

- **Không** commit thẳng vào `main` hoặc `develop`
- **Không** force push (`git push --force`) lên nhánh chia sẻ
- **Không** commit file chứa thông tin nhạy cảm (`.env`, API key, mật khẩu)
- **Không** merge PR khi chưa có approval
- **Không** xóa lịch sử commit bằng `rebase` trên nhánh đã được push

### Luôn Luôn Phải

- **Luôn** tạo nhánh mới cho mỗi tính năng/sửa lỗi
- **Luôn** pull code mới nhất trước khi bắt đầu làm việc
- **Luôn** viết commit message rõ ràng, có ý nghĩa
- **Luôn** đảm bảo code build thành công và pass test trước khi tạo PR
- **Luôn** xóa nhánh sau khi đã merge

### Bảo Vệ Nhánh Chính

Cấu hình trên GitHub/GitLab để bảo vệ nhánh `main` và `develop`:

- Yêu cầu ít nhất 1 approval trước khi merge
- Bật kiểm tra CI/CD tự động (build, test, lint)
- Không cho phép commit thẳng (direct push)
- Yêu cầu nhánh phải cập nhật với nhánh gốc trước khi merge

---

## Tham Khảo Nhanh - Các Lệnh Thường Dùng

```bash
# Xem trạng thái
git status
git log --oneline --graph --all

# Quản lý nhánh
git branch -a                          # liệt kê tất cả nhánh
git checkout -b feature/ten-nhanh      # tạo và chuyển nhánh mới
git branch -d ten-nhanh                # xóa nhánh local

# Đồng bộ
git fetch origin                       # tải về thay đổi (không merge)
git pull origin develop                # tải và merge
git push origin feature/ten-nhanh     # đẩy nhánh lên remote

# Stash (lưu tạm thời)
git stash                              # lưu thay đổi chưa commit
git stash pop                          # lấy lại thay đổi đã lưu
git stash list                         # xem danh sách stash

# Undo
git restore <file>                     # hủy thay đổi chưa staged
git restore --staged <file>            # bỏ file khỏi staging
git revert <commit-hash>               # tạo commit đảo ngược (an toàn)
```

---

*Tài liệu này được tạo ngày 16/09/2026. Cập nhật khi có thay đổi về quy trình.*
