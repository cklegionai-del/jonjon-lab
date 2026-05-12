# 🇹🇳 فاتورة تونس - Tunisian E-Invoicing System (TEIF v1.8.7)

نظام شامل للفوترة الإلكترونية التونسية المتوافق مع معيار TEIF v1.8.7

A complete Tunisian e-invoicing CLI tool compliant with TEIF v1.8.7 standard.

---

## ✨ الميزات | Features

- ✅ **توليد XML** متوافق مع TEIF v1.8.7
- 🔐 **توقيع رقمي** RSA-SHA256 + XMLDSig
- 🧩 **QR Code** بترميز TLV (VAT + Timestamp + Amount + Signature)
- 📄 **PDF احترافي** بالعربية والفرنسية
- 🚀 **CLI سهل** الاستعمال
- 🔗 **جاهز للإرسال** لمنصة فاتورة (TTN API)

---

## 📦 التثبيت | Installation

### المتطلبات | Requirements
- Node.js v18+ 
- npm أو yarn

```bash
# انسخ المشروع
git clone https://github.com/YOUR_USERNAME/jonjon-lab.git
cd jonjon-lab

# ثبّت الاعتماديات
npm install