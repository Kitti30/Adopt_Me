🐾 Adopt Me — ระบบหาบ้านให้สัตว์จรจัด

### สำหรับผู้ตรวจ

```bash
git clone https://github.com/Kitti30/Adopt_Me.git
cd Adopt_Me
docker compose --profile monitoring up -d --build
```
http://localhost:8000
http://localhost:9090/targets
http://localhost:3000

### บัญชีทดลอง รหัสผ่านทุกบัญชี: `Demo12345!`

| `admin` | ทีมงาน + ผู้ดูแลระบบ | หน้าตรวจคำขอ และหน้าแอดมิน
| `owner1` | ผู้ลงประกาศสัตว์ | ลงทะเบียนสัตว์
| `somchai` | ผู้ขอรับเลี้ยง | ยื่นคำขอ ดูสถานะ 

###
Grafana admin / admin
### เครื่องมือเสริม
```bash
docker compose exec web python manage.py test                  # รันชุดทดสอบ
docker compose --profile monitoring up -d --build              # เปิด Prometheus (:9090) และ Grafana (:3000, admin/admin)
docker compose down                                            # หยุดระบบ (เพิ่ม -v เพื่อล้างข้อมูล)
```
