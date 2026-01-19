# 🖱️ AutoClickerGUI-Linux

Aplikasi **Auto Clicker** yang powerful untuk Linux dengan dukungan **Flatpak**, window detection, dan background mode. Dapat merekam dan memutar klik mouse secara otomatis pada aplikasi target dengan konfigurasi yang fleksibel.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange?logo=linux)](https://www.linux.org/)

---

## ✨ Fitur Utama

- 🎯 **Rekam & Putar Otomatis** - Rekam klik mouse dan putar kembali pada jendela target
- 🔄 **Multi-Method Window Detection** - Deteksi jendela dengan 4 metode fallback (Xlib, wmctrl, xdotool, Manual)
- 📦 **Flatpak Compatible** - Dukungan penuh untuk aplikasi Flatpak di sandbox
- 🌙 **Background Mode** - Jalankan auto clicker di background tanpa GUI
- ⌨️ **Global Hotkeys** - Kontrol dengan tombol keyboard global (Start/Stop/Pause)
- 🎨 **Custom GUI** - Interface modern dengan ttkbootstrap themes
- 💾 **Save & Load Macros** - Simpan dan muat konfigurasi klik dalam format JSON
- ⚙️ **Settings Manager** - Pengaturan persisten untuk theme, hotkeys, dan preferensi
- 🔧 **Event Editing** - Edit atau hapus individual events dalam macro
- 📊 **Macro Manager** - Kelola multiple macros dengan mudah

---

## 📋 Requirements

### Sistem
- **OS**: Linux (Ubuntu, Debian, Fedora, Arch, dll)
- **Python**: 3.8 atau lebih tinggi
- **X11**: System harus menggunakan X11 (tidak support Wayland penuh)

### Dependencies
```bash
ttkbootstrap    # Modern GUI toolkit
pynput          # Input simulation & monitoring
python-xlib     # X11 library untuk window detection
wmctrl          # Window manager control (optional tapi recommended)
xdotool         # X11 automation tool (optional tapi recommended)
```

---

## 🚀 Instalasi & Setup

### 1. Clone atau Download Repository

```bash
cd ~/Documents
git clone https://github.com/andrew7str/AutoClickerGUI-Linux.git
cd AutoClickerGUI-Linux
```

### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install wmctrl python3-xlib xdotool python3-pip python3-venv
```

**Fedora:**
```bash
sudo dnf install wmctrl python3-xlib xdotool python3-pip
```

**Arch Linux:**
```bash
sudo pacman -S wmctrl python3-xlib xdotool
```

### 3. Setup Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 💻 Cara Menggunakan

### Menjalankan Aplikasi

```bash
cd AutoClickerGUI-Linux
chmod +x run_app.sh
sudo ./run_app.sh
```

### Workflow Dasar

#### 1. **Memilih Target Window**
```
Click → "Select Target Window" 
        ↓
        Pilih window dari list atau gunakan "Manual Select"
        ↓
        Click "OK"
```

#### 2. **Merekam Klik Mouse**
- Click tombol **"Start Recording"**
- Lakukan klik mouse yang ingin direkam pada target window
- Click tombol **"Stop Recording"** ketika selesai
- Preview events di list

#### 3. **Memutar Klik**
- Click tombol **"Play"**
- Macro akan dieksekusi pada target window
- Gunakan hotkey untuk pause/resume atau stop

#### 4. **Menyimpan & Memuat**
- **Save Macro**: File → Save Macro (format JSON)
- **Load Macro**: File → Open Macro (baca JSON)
- Macro akan tersimpan di folder project

---

## ⌨️ Keyboard Shortcuts & Hotkeys

### Default Global Hotkeys
- **Ctrl+F6**: Start playback
- **Ctrl+F7**: Stop playback  
- **Ctrl+F8**: Pause/Resume

*Hotkeys dapat dikonfigurasi di Settings*

### GUI Shortcuts
- **File Menu**: Ctrl+O (Open), Ctrl+S (Save)
- **Spacebar**: Toggle recording/playback

---

## 🔧 Konfigurasi & Settings

### Mengakses Settings

Klik menu **"Settings"** atau gunakan shortcut untuk:

#### Theme Selection
- Pilih dari berbagai tema ttkbootstrap (litera, darkly, superhero, dll)

#### Hotkey Configuration
- Customize global hotkeys untuk Start, Stop, Pause
- Format: `Ctrl+Key`, `Alt+Key`, `Shift+Key`

#### Auto-Click Parameters
- Interval antar klik (ms)
- Jumlah repetisi
- Delay sebelum start

#### Window Selection Method
- Pilih metode deteksi window (Xlib, wmctrl, xdotool, Manual)

### Settings File

Settings tersimpan di `settings.json`:

```json
{
  "theme": "litera",
  "hotkey_start": "ctrl+f6",
  "hotkey_stop": "ctrl+f7",
  "hotkey_pause": "ctrl+f8",
  "click_interval": 100,
  "repeat_count": 1,
  "initial_delay": 1
}
```

---

## 🎯 Advanced Features

### Background Mode

Jalankan auto clicker tanpa GUI untuk performa maksimal:

```bash
python background_player.py macro.json --target-window "Firefox" --loop
```

Opsi:
- `--target-window NAME`: Nama jendela target
- `--loop`: Ulangi terus-menerus
- `--repeat N`: Ulangi N kali

### Manual Window Selection

Jika deteksi otomatis gagal (khususnya di Flatpak):
1. Click "Select Target Window"
2. Click tombol **"Manual Select"**
3. Click pada jendela target
4. Jendela akan otomatis terdeteksi

### Event Editing

Setelah merekam:
1. Klik pada event di list
2. Click "Edit Event"
3. Ubah koordinat X, Y atau timestamp
4. Click "Save"

Atau hapus event dengan tombol "Remove Event"

### Flatpak Support

Aplikasi secara otomatis mendeteksi Flatpak environment:

```
Deteksi → Is Flatpak? 
    ↓ YES
    Try wmctrl (Flatpak-safe)
    ↓ 
    Try xdotool
    ↓
    Fallback ke Manual Selection
```

---

## 📁 Project Structure

```
AutoClickerGUI-Linux-Pro/
├── main.py                    # Main GUI application
├── main_v1.py                # Alternative version
├── background_player.py       # CLI for background mode
├── recorder.py               # Mouse event recorder
├── player.py                 # Event playback engine
├── window_selector.py        # Window detection & selection UI
├── hotkey_listener.py        # Global hotkey listener
├── settings_manager.py       # Settings persistence
├── settings_window.py        # Settings UI
├── edit_window.py            # Event editing UI
├── add_event_dialog.py       # Add event dialog
│
├── requirements.txt          # Python dependencies
├── settings.json             # User settings
├── TEST-Macro.json           # Example macro file
│
├── README.md                 # Documentation (this file)
├── ARCHITECTURE.md           # System architecture
├── IMPLEMENTATION_SUMMARY.md # Implementation details
├── QUICK_START.md           # Quick reference
└── venv/                    # Python virtual environment
```

### Core Modules

**recorder.py**
- Merekam mouse events (click, move, scroll)
- Simpan timestamp untuk akurasi timing
- Filter events berdasarkan jendela target

**player.py**
- Main playback engine
- Kontrol kecepatan playback
- Support pause/resume/stop

**window_selector.py**
- Multi-method window detection
- Xlib, wmctrl, xdotool fallback
- Manual click-to-select

**hotkey_listener.py**
- Global hotkey listener menggunakan pynput
- Background thread monitoring
- Customizable shortcuts

**settings_manager.py**
- Load/save settings ke JSON
- Default values management
- Type validation

---

## 🐛 Troubleshooting

### Problem: "No windows detected"

**Solusi:**
1. Install dependencies:
   ```bash
   sudo apt install wmctrl xdotool python3-xlib
   ```

2. Verifikasi tools bekerja:
   ```bash
   wmctrl -l          # List windows
   xdotool search .   # Search windows
   ```

3. Gunakan Manual Select:
   - Click "Select Target Window"
   - Click tombol "Manual Select"
   - Click pada jendela target

### Problem: Macro tidak berjalan pada window target

**Solusi:**
1. Pastikan window sudah terfokus
2. Check window title di "Select Target Window"
3. Coba delay awal yang lebih panjang di Settings
4. Verifikasi koordinat X,Y sudah benar

### Problem: Global hotkeys tidak bekerja

**Solusi:**
1. Check Settings untuk hotkey configuration
2. Pastikan tidak ada aplikasi lain menggunakan hotkey yang sama
3. Jalankan aplikasi dengan privilege yang tepat
4. Coba gunakan kombinasi key yang berbeda

### Problem: Flatpak app tidak terdeteksi

**Solusi:**
1. Flatpak apps perlu X11 socket access
2. Gunakan Manual Select method
3. Verifikasi Flatpak permission:
   ```bash
   flatpak info --show-permissions com.app.name
   ```

### Problem: Koordinat klik tidak akurat

**Solusi:**
1. Screenshot window saat merekam
2. Pastikan window tidak berubah ukuran
3. Edit klik secara manual dengan coordinates yang tepat
4. Perhatikan DPI scaling

---

## 🔍 Testing & Debugging

### Test Window Detection

```bash
python test_window_detection.py
```

Output akan menampilkan status keempat detection methods.

### Test Pynput

```bash
python test_pynput.py
```

Verifikasi mouse input working properly.

### Debug Mode

Edit `main.py` dan uncomment debug prints:

```python
# DEBUG: Print detected windows
print(f"Detected windows: {self.windows}")

# DEBUG: Print mouse events
print(f"Event: {x}, {y}, {button}")
```

---

## 📊 Use Cases

### 1. **Automated Game Clicking**
- Farming games repetitif
- Koleksi resources otomatis
- Testing game mechanics

### 2. **Data Entry Automation**
- Fill form fields dengan pola
- Database entry testing
- Repetitive data input

### 3. **Testing & QA**
- UI test automation
- Regression testing
- Load testing dengan multiple clicks

### 4. **Productivity Tools**
- Auto-responder untuk apps
- Scheduled automatic tasks
- Accessibility features

---

## ⚠️ Ethical & Legal Disclaimer

**IMPORTANT**: Gunakan aplikasi ini secara **bertanggung jawab**:

✅ **Boleh digunakan untuk:**
- Testing aplikasi sendiri
- Automation tasks personal
- Accessibility purposes
- Productivity tools

❌ **Jangan digunakan untuk:**
- Cheat di online games
- Hack akun orang lain
- Spam atau harassment
- Bypass security measures
- Melanggar Terms of Service

**Pengguna bertanggung jawab** atas penggunaan aplikasi ini. Penulis tidak bertanggung jawab atas penyalahgunaan.

---

## 🤝 Contributing

Kontribusi sangat diterima! Silakan:

1. Fork repository
2. Buat branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buka Pull Request

### Reporting Bugs

Jika menemukan bug, buat issue dengan:
- Deskripsi bug
- Steps untuk reproduce
- Expected vs actual behavior
- Environment info (OS, Python version, GUI)

---

## 📝 Version History

- **v1.0** - Initial release
- **v2.0** - Added Flatpak support
- **v2.1** - Added background mode
- **v2.2** - Added event editing & settings manager
- **Pro** - Latest version dengan all features

---

## 📄 License

Project ini dilisensikan di bawah **MIT License** - lihat file [LICENSE](LICENSE) untuk details.

---

## 🙏 Acknowledgments

- **ttkbootstrap** - Modern GUI toolkit
- **pynput** - Input simulation library
- **Xlib** - X11 protocol library
- **wmctrl** & **xdotool** - Window management tools

---

## 📮 Contact & Support

- **GitHub Issues**: Report bugs dan request features
- **Documentation**: Lihat ARCHITECTURE.md dan IMPLEMENTATION_SUMMARY.md
- **Quick Help**: Lihat QUICK_START.md

---

## 🎓 Learning Resources

Ingin belajar cara kerja aplikasi?

- [ARCHITECTURE.md](ARCHITECTURE.md) - Diagram sistem & flow
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Detail implementasi
- [Code Comments](main.py) - Inline documentation

---

**Last Updated**: January 2026  
**Maintained by**: Community Contributors  
**Status**: Active Development 🚀
