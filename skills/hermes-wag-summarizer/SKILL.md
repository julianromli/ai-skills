---
name: hermes-wag-summarizer
description: Plug & play skill untuk membuat cronjob summary grup WhatsApp secara otomatis menggunakan Hermes WhatsApp Bridge.
version: 1.0.0
metadata:
  hermes:
    tags: [whatsapp, cron, summary, digest, group, plug-and-play]
    related_skills: [whatsapp-bridge-watchdog, whatsapp-bridge-diagnostics]
---

# Hermes WAG Summarizer

Skill ini menyediakan **solusi lengkap dan plug & play** untuk membuat cronjob yang secara otomatis merangkum percakapan grup WhatsApp.

## Tujuan Skill

- Memberikan cara **paling sederhana** untuk user Hermes baru agar bisa langsung punya fitur summary grup WhatsApp.
- Menjadi **single source of truth** untuk semua hal terkait WhatsApp Group Summarizer.
- Mendukung **multiple grup** dengan konfigurasi terpisah.
- Default delivery ke grup WhatsApp yang sama.

## Fitur Utama

- Setup summary grup dalam hitungan menit
- Support multiple grup WhatsApp
- Prompt yang sudah dioptimalkan untuk WhatsApp
- Struktur output yang konsisten dan enak dibaca
- Auto `[SILENT]` ketika tidak ada aktivitas
- Panduan troubleshooting lengkap

## Cara Menggunakan (Plug & Play)

### 1. Install Skill

```bash
hermes skills install hermes-wag-summarizer
```

### 2. Buat Wrapper untuk Grup Baru

Gunakan script helper untuk membuat wrapper script baru:

```bash
python3 ~/.hermes/skills/hermes-wag-summarizer/scripts/create-group-wrapper.py \
  --chat-id "120363402262217562@g.us" \
  --group-name "VibeDev ID" \
  --hours 12
```

Script ini akan otomatis membuat:
- Wrapper script di `~/.hermes/scripts/`
- Entry di tabel konfigurasi

### 3. Buat Cronjob

```bash
hermes cron create \
  --name "VibeDev ID Summary" \
  --script "~/.hermes/scripts/vibedev-id-summary.py" \
  --schedule "0 5,17 * * *" \
  --deliver "whatsapp:120363402262217562@g.us"
```

### 4. (Opsional) Custom Prompt

Jika ingin mengubah gaya ringkasan, edit file prompt:

```bash
~/.hermes/skills/hermes-wag-summarizer/prompts/default-summary-prompt.txt
```

Lalu arahkan cronjob ke prompt tersebut.

## Struktur Output yang Direkomendasikan

```
*Ringkasan VibeDev ID (12 jam terakhir)*

*Topik yang Dibahas:*
• ...

*Highlight Penting:*
• ...

*Pertanyaan yang Masih Terbuka:*
• ...

*Link / Resource:*
• ...

```

## Konfigurasi Default

| Pengaturan | Nilai Default | Keterangan |
|------------|---------------|----------|
| Window | 12 jam | Bisa diubah per grup |
| Delivery | Ke grup yang sama | Kecuali explicit minta ke tempat lain |
| Format | Markdown WhatsApp | `*teks*` untuk bold |
| Empty Window | `[SILENT]` | Tidak spam grup |
| Schedule | `0 5,17 * * *` | 05:00 & 17:00 UTC |

## File yang Disertakan

- `scripts/whatsapp-group-summary.py` — Parser utama
- `scripts/create-group-wrapper.py` — Helper membuat wrapper baru
- `prompts/default-summary-prompt.txt` — Prompt default yang sudah dioptimalkan
- `examples/` — Contoh konfigurasi cronjob

## Catatan Penting

- Skill ini **hanya untuk summary**. Untuk moderation atau analytics, gunakan skill terpisah.
- Pastikan WhatsApp Bridge sudah berjalan dan `messages.jsonl` aktif.
- Untuk troubleshooting bridge yang "deaf", gunakan skill `whatsapp-bridge-watchdog`.

## Maintenance

Setelah menambah atau mengubah grup, update bagian **Live Inventory** di skill ini agar tetap menjadi single source of truth.
