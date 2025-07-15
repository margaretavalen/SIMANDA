import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask import Response
from werkzeug.utils import secure_filename
from datetime import date
from datetime import datetime
import mysql.connector
import pickle
import base64
import bcrypt
import re

app = Flask(__name__)
app.secret_key = 'loginSIMANDA'  # Untuk session dan flash

# Fungsi buka koneksi MySQL
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # sesuaikan
        database='magang_db'
    )
    return connection

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ambil data status magang
    cursor.execute("SELECT COUNT(*) FROM peserta_magang WHERE status = 'Selesai Magang'")
    selesai_magang = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM peserta_magang WHERE status = 'Sedang Magang'")
    sedang_magang = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM peserta_magang WHERE status = 'Akan Magang'")
    akan_magang = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM peserta_magang WHERE status = 'Batal Magang'")
    batal_magang = cursor.fetchone()[0]

    # Map bidang sesuai permintaan
    bidang_map = {
        "Bidang 1": "Pengembangan Komunikasi Publik",
        "Bidang 2": "Sistem Pemerintahan",
        "Bidang 3": "Pengelolaan Informasi",
        "Bidang 4": "Infrastruktur",
        "Bidang 5": "Statistik",
        "Sekretariat": "Sekretariat"
    }

    jumlah_per_bidang = {}
    for key, label in bidang_map.items():
        cursor.execute("SELECT COUNT(*) FROM peserta_magang WHERE bidang = %s", (key,))
        jumlah_per_bidang[label] = cursor.fetchone()[0]

    conn.close()

    return render_template("index.html",
        selesai_magang=selesai_magang,
        sedang_magang=sedang_magang,
        akan_magang=akan_magang,
        batal_magang=batal_magang,
        jumlah_per_bidang=jumlah_per_bidang
    )
    
@app.route('/loginregister', methods=['GET', 'POST'])
def loginregister():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if 'login' in request.form:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = user['username']
                session['nama'] = user.get('nama', user['username'])  
                if user['username'] == 'admin':
                    session['role'] = 'admin'
                    cursor.close()
                    conn.close()
                    return redirect(url_for('admin'))
                else:
                    session['role'] = 'user'
                    cursor.close()
                    conn.close()
                    return redirect(url_for('dashboard'))

                flash('Username atau password salah!', 'danger')

        elif 'register' in request.form:
            confirm_password = request.form.get('confirm_password')
            if password != confirm_password:
                flash('Konfirmasi password tidak cocok!', 'danger')
            else:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                existing = cursor.fetchone()
                if existing:
                    flash('Username sudah terdaftar! Silakan login.', 'warning')
                elif not re.match(r'^[A-Za-z0-9]+$', username):
                    flash('Username hanya boleh berisi huruf dan angka!', 'warning')
                else:
                    try:
                        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                        conn.commit()
                        flash('Registrasi berhasil! Silakan login.', 'success')
                        cursor.close()
                        conn.close()
                        return redirect(url_for('loginregister'))
                    except Exception as e:
                        conn.rollback()
                        flash(f'Error saat menyimpan ke database: {e}', 'danger')

        cursor.close()
        conn.close()

    return render_template('login_register.html')

# USER

@app.route('/login/dashboard')
def dashboard():
    if 'username' in session and session.get('role') == 'user':
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT YEAR(tgl_masuk) AS tahun, COUNT(*) AS jumlah
            FROM peserta_magang
            GROUP BY YEAR(tgl_masuk)
            ORDER BY YEAR(tgl_masuk)
        """
        cursor.execute(query)
        results = cursor.fetchall()

        labels = [str(row[0]) for row in results]
        data = [row[1] for row in results]

        cursor.execute("SELECT COUNT(*) FROM peserta_magang")
        total_peserta = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT asal) FROM peserta_magang")
        total_universitas = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return render_template('dashboard.html',
                               username=session['username'],
                               labels=labels,
                               data=data,
                               total_peserta=total_peserta,
                               total_universitas=total_universitas)
    else:
        flash('Silahkan login dulu!', 'danger')
        return redirect(url_for('loginregister'))
        
@app.route('/gambar/<int:id>')
def gambar(id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT profil FROM peserta_magang WHERE id = %s", (id,))
        result = cursor.fetchone()
        if result and result[0]:
            return Response(result[0], mimetype='image/jpeg')  # atau 'image/png' jika perlu
        else:
            # Kalau tidak ada gambar, tampilkan gambar default dari /static
            return redirect(url_for('static', filename='uploads/default.jpg'))
    except Exception as e:
        app.logger.error(f"Error fetching image: {str(e)}")
        return '', 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/login/data')
def data():
    if 'username' in session and session.get('role') == 'user':
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM peserta_magang")
            data = cursor.fetchall()
        except Exception as e:
            app.logger.error(f"Error in /data route: {str(e)}")
            flash('Terjadi kesalahan saat mengambil data.', 'danger')
            data = []  # agar template tetap bisa render
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return render_template('data.html', username=session['username'], data=data)
    else:
        flash('Silahkan login terlebih dahulu!', 'danger')
        return redirect(url_for('loginregister'))

@app.route('/login/penugasan')
def penugasan():
    if 'username' in session and session.get('role') == 'user':
        username = session['username']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT nama FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            nama = user['nama']
        else:
            nama = ''

        return render_template('penugasan.html', nama=nama, username=username)
    else:
        flash('Silahkan login terlebih dahulu!', 'danger')
        return redirect(url_for('loginregister'))

@app.route('/get_tanggal_user')
def get_tanggal_user():
    nama_user = session.get('username')
    if not nama_user:
        return jsonify([])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT tanggal, username FROM penugasan WHERE tanggal IS NOT NULL AND username = %s",
        (nama_user,)
    )
    results = cursor.fetchall()
    
    
    tanggal_list = [
        {
            "start": row[0].strftime('%Y-%m-%d'),
            "color": "#007bff"  
        }
        for row in results if row[0] is not None
    ]

    cursor.close()
    conn.close()

    return jsonify(tanggal_list)
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@app.route('/upload', methods=['POST'])
def upload():
    if 'files[]' not in request.files:
        flash('Tidak ada file yang diupload.', 'danger')
        return redirect(url_for('penugasan'))

    username = request.form.get('username', '').strip()
    nama = request.form.get('nama', '').strip()
    asal = request.form.get('asal', '').strip()
    bidang = request.form.get('bidang', '').strip()
    tanggal_str = request.form.get('tanggal', '').strip()
    files = request.files.getlist('files[]')

    if not bidang or not asal or not tanggal_str:
        flash('Semua kolom harus diisi.', 'danger')
        return redirect(url_for('penugasan'))

    if len(files) != 3:
        flash('Harap upload tepat 3 file.', 'danger')
        return redirect(url_for('penugasan'))

    # Cek size file per file
    for file in files:
        if not file or file.filename == '':
            flash('Ada file kosong.', 'danger')
            return redirect(url_for('penugasan'))

        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > 5 * 1024 * 1024:
            flash(f'File {file.filename} melebihi 5 MB.', 'danger')
            return redirect(url_for('penugasan'))

    filedatas = [f.read() for f in files]
    total_size = sum(len(data) for data in filedatas)
    if total_size > 10 * 1024 * 1024:
        flash('Total ukuran file melebihi 10 MB.', 'danger')
        return redirect(url_for('penugasan'))

    try:
        tanggal_obj = datetime.strptime(tanggal_str, '%Y-%m-%d')
    except ValueError:
        flash('Format tanggal salah.', 'danger')
        return redirect(url_for('penugasan'))

    filenames = [secure_filename(f.filename) for f in files]
    filedatas = [f.read() for f in files]

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO penugasan
            (username, nama, asal, bidang, tanggal, 
             filename, file_data, filename2, file_data2, filename3, file_data3)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (username, nama, asal, bidang, tanggal_obj,
               filenames[0], filedatas[0],
               filenames[1], filedatas[1],
               filenames[2], filedatas[2])

        cursor.execute(sql, val)
        conn.commit()
        flash('Penugasan berhasil diupload.', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Gagal upload: {e}', 'danger')

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('penugasan'))

@app.route('/contact')
def contact_public():
    return render_template('contact.html')

# Kontak versi khusus untuk user login
@app.route('/login/contact')
def contact_user():
    if 'username' in session and session.get('role') == 'user':
        return render_template('contact.html', username=session['username'])
    else:
        flash('Silahkan login dulu untuk mengakses halaman kontak khusus.', 'warning')
        return redirect(url_for('loginregister'))

# ADMIN

@app.route('/login/admin')
def admin():
    if 'username' in session and session.get('role') == 'admin':
        conn = get_db_connection()
        cursor = conn.cursor()

        # Jumlah total peserta magang
        cursor.execute("SELECT COUNT(*) FROM peserta_magang")
        semua_magang = cursor.fetchone()[0]

        # Jumlah per status
        cursor.execute("SELECT COUNT(*) FROM peserta_magang WHERE status = 'Selesai Magang'")
        selesai_magang = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM peserta_magang WHERE status = 'Sedang Magang'")
        sedang_magang = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM peserta_magang WHERE status = 'Akan Magang'")
        akan_magang = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM peserta_magang WHERE status = 'Batal Magang'")
        batal_magang = cursor.fetchone()[0]

        # Jumlah per bidang
        bidang_map = {
            "Bidang 1": "Pengembangan Komunikasi Publik",
            "Bidang 2": "Sistem Pemerintahan",
            "Bidang 3": "Pengelolaan Informasi",
            "Bidang 4": "Infrastruktur",
            "Bidang 5": "Statistik",
            "Sekretariat": "Sekretariat"
        }

        jumlah_per_bidang = {}
        for key, label in bidang_map.items():
            cursor.execute("SELECT COUNT(*) FROM peserta_magang WHERE status = 'Sedang Magang' AND bidang = %s", (key,))
            jumlah_per_bidang[label] = cursor.fetchone()[0]

        # Grafik jumlah peserta magang per bulan
        cursor.execute("""
            SELECT 
                MONTHNAME(tgl_masuk) AS bulan,
                COUNT(*) AS jumlah
            FROM peserta_magang
            GROUP BY MONTH(tgl_masuk)
            ORDER BY MONTH(tgl_masuk)
        """)
        chart_data = cursor.fetchall()
        labels = [row[0] for row in chart_data]  # bulan
        data = [row[1] for row in chart_data]    # jumlah

        chart_pairs = list(zip(labels, data))

        conn.close()

        return render_template("admin/index_admin.html",
            semua_magang=semua_magang,
            selesai_magang=selesai_magang,
            sedang_magang=sedang_magang,
            akan_magang=akan_magang,
            batal_magang=batal_magang,
            jumlah_per_bidang=jumlah_per_bidang,
            chart_labels=labels,
            chart_data=data,
            chart_pairs=chart_pairs
        )
    else:
        flash('Akses khusus admin!', 'danger')
        return redirect(url_for('loginregister'))

@app.route('/login/data_admin')
def dataAdmin():
    if 'username' in session and session.get('role') == 'admin':
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            today = date.today()

            # Update status otomatis berdasarkan tanggal
            cursor.execute("""
                UPDATE peserta_magang
                SET status = CASE
                    WHEN tgl_masuk > %s THEN 'Akan Magang'
                    WHEN tgl_masuk <= %s AND tgl_keluar >= %s THEN 'Sedang Magang'
                    WHEN tgl_keluar < %s THEN 'Selesai Magang'
                    ELSE status
                END
                WHERE status != 'Batal Magang'
            """, (today, today, today, today))
            conn.commit()

            cursor.execute("SELECT * FROM peserta_magang")
            semua_data = cursor.fetchall()

            # Filter berdasarkan status
            akan_magang = [row for row in semua_data if row['status'] == 'Akan Magang']
            sedang_magang = [row for row in semua_data if row['status'] == 'Sedang Magang']
            selesai_magang = [row for row in semua_data if row['status'] == 'Selesai Magang']
            batal_magang = [row for row in semua_data if row['status'] == 'Batal Magang']

        except Exception as e:
            app.logger.error(f"Error in /login/data_admin route: {str(e)}")
            flash('Terjadi kesalahan saat mengambil data.', 'danger')
            akan_magang, sedang_magang, selesai_magang, batal_magang = [], [], [], []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return render_template(
            'admin/data_admin.html',
            username=session['username'],
            akan_magang=akan_magang,
            sedang_magang=sedang_magang,
            selesai_magang=selesai_magang,
            batal_magang=batal_magang,
            dataAdmin=True
        )
    else:
        flash('Akses khusus admin!', 'danger')
        return redirect(url_for('loginregister'))

@app.route('/login/data_user')
def dataUser():
    if 'username' in session and session.get('role') == 'admin':
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users")
            semua_data = cursor.fetchall()

        except Exception as e:
            app.logger.error(f"Error in /login/data_user route: {str(e)}")
            flash('Terjadi kesalahan saat mengambil data.', 'danger')

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return render_template(
            'admin/data_user.html',
            nama=session['nama'],
            username=session['username'],
            dataUser=True,
            semua_data=semua_data  
        )

    else:
        flash('Akses khusus admin!', 'danger')
        return redirect(url_for('loginregister'))

@app.route('/batal_magang/<int:peserta_id>', methods=['POST'])
def batal_magang(peserta_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE peserta_magang SET status = 'Batal Magang' WHERE id = %s", (peserta_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Status peserta diubah menjadi Batal Magang', 'warning')
    return redirect(url_for('dataAdmin'))

# Tampilkan form edit
@app.route('/form_edit/<int:id>', methods=['GET'])
def form_edit(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM peserta_magang WHERE id = %s", (id,))
    peserta = cursor.fetchone()
    cursor.close()
    conn.close()
    if peserta:
        return render_template('admin/form_edit.html', peserta=peserta)
    else:
        flash('Data peserta tidak ditemukan.', 'danger')
        return redirect(url_for('dataAdmin'))

# Simpan hasil update
@app.route('/update/<int:id>', methods=['POST'])
def update_peserta(id):
    nama = request.form['nama']
    asal = request.form['asal']
    jurusan = request.form['jurusan']
    tgl_masuk = request.form['tgl_masuk']
    tgl_keluar = request.form['tgl_keluar']
    bidang = request.form['bidang']

    foto_file = request.files.get('profil')

    conn = get_db_connection()
    cursor = conn.cursor()

    if foto_file and foto_file.filename != '':
        foto_data = foto_file.read()
        cursor.execute("""
            UPDATE peserta_magang
            SET nama=%s, asal=%s, jurusan=%s, tgl_masuk=%s, tgl_keluar=%s, bidang=%s, profil=%s
            WHERE id=%s
        """, (nama, asal, jurusan, tgl_masuk, tgl_keluar, bidang, foto_data, id))
    else:
        cursor.execute("""
            UPDATE peserta_magang
            SET nama=%s, asal=%s, jurusan=%s, tgl_masuk=%s, tgl_keluar=%s, bidang=%s
            WHERE id=%s
        """, (nama, asal, jurusan, tgl_masuk, tgl_keluar, bidang, id))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Data peserta berhasil diperbarui', 'success')
    return redirect(url_for('dataAdmin'))

@app.route('/form_tambah')
def form_tambah():
    return render_template('admin/form_tambah.html')

@app.route('/predict_bidang', methods=['POST'])
def predict_bidang():
    data = request.get_json()
    jurusan = data.get('jurusan')

    if not jurusan:
        return jsonify({'bidang': 'Input kosong'}), 400

    try:
        with open('model_penempatan.pkl', 'rb') as file:
            bundle = pickle.load(file)

        model = bundle['model']
        vectorizer = bundle['vectorizer']
        label_encoder = bundle['label_encoder']

        input_vec = vectorizer.transform([jurusan])
        pred_encoded = model.predict(input_vec)[0]
        bidang_prediksi = label_encoder.inverse_transform([pred_encoded])[0]

    except Exception as e:
        print("Error saat prediksi:", e)
        bidang_prediksi = 'Prediksi gagal'

    return jsonify({'bidang': bidang_prediksi})

@app.route('/tambah', methods=['POST'])
def tambah_peserta():
    nama = request.form['nama'].strip()
    asal = request.form['asal'].strip()
    jurusan = request.form['jurusan'].strip()
    tgl_masuk = request.form['tgl_masuk'].strip()
    tgl_keluar = request.form['tgl_keluar'].strip()
    bidang = request.form.get('bidang')

    foto_file = request.files.get('profil')
    foto_data = None

    # Cek file upload
    if foto_file and foto_file.filename != '':
        foto_file.seek(0, 2)  # pindah ke ujung file
        file_size = foto_file.tell()
        foto_file.seek(0)     # balik ke awal file lagi

        max_size = 2 * 1024 * 1024  # 2 MB

        if file_size > max_size:
            flash('Ukuran file terlalu besar! Maksimal 2MB.', 'danger')
            return redirect(url_for('form_tambah'))  

        foto_data = foto_file.read()  # kalau mau simpan di BLOB

    # Validasi field wajib
    if not nama or not asal or not jurusan or not tgl_masuk or not tgl_keluar:
        flash('Semua kolom wajib diisi!', 'danger')
        return redirect(url_for('form_tambah'))

    today = date.today()
    masuk = date.fromisoformat(tgl_masuk)
    keluar = date.fromisoformat(tgl_keluar)

    if masuk > today:
        status = 'Akan Magang'
    elif masuk <= today <= keluar:
        status = 'Sedang Magang'
    else:
        status = 'Selesai Magang'

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO peserta_magang (nama, asal, jurusan, tgl_masuk, tgl_keluar, bidang, profil, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (nama, asal, jurusan, tgl_masuk, tgl_keluar, bidang, foto_data, status))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Peserta berhasil ditambahkan', 'success')
    return redirect(url_for('dataAdmin'))

@app.route('/form_tambah_user')
def form_tambah_user():
    return render_template('admin/form_tambah_user.html')

@app.route('/tambah_user', methods=['POST'])
def tambah_user():
    if 'username' in session and session.get('role') == 'admin':
        nama = request.form['nama']
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (nama, username, password)
            VALUES (%s, %s, %s)
        """, (nama, username, password))
        conn.commit()
        cursor.close()
        conn.close()

        flash('User berhasil ditambahkan', 'success')
        return redirect(url_for('dataUser'))
    else:
        flash('Akses khusus admin!', 'danger')
        return redirect(url_for('loginregister'))

@app.route('/login/penugasan_admin', methods=['GET', 'POST'])
def penugasan_admin():
    if 'username' in session and session.get('role') == 'admin':
        conn = None
        cursor = None
        tanggal = None
        data_penugasan = []
        data_belum_ada_tugas = []

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Ambil tanggal dari form POST atau query GET, default hari ini
            if request.method == 'POST':
                tanggal = request.form.get('tanggal')
            else:
                tanggal = request.args.get('tanggal')

            if not tanggal:
                tanggal = datetime.today().strftime('%Y-%m-%d')

            # Ambil data penugasan sesuai tanggal, hanya untuk peserta yang ada di peserta_magang
            cursor.execute("""
                SELECT p.id_tugas, p.nama, p.bidang,
                    p.file_data, p.file_data2, p.file_data3, p.tanggal
                FROM penugasan p
                INNER JOIN peserta_magang m ON p.nama = m.nama
                WHERE DATE(p.tanggal) = %s
                ORDER BY p.nama
            """, (tanggal,))
            rows = cursor.fetchall()


            for no, row in enumerate(rows, start=1):
                data_penugasan.append({
                    "no": no,
                    "id_tugas": row["id_tugas"],
                    "nama": row["nama"],
                    "bidang": row["bidang"],
                    "img1": bool(row["file_data"]),
                    "img2": bool(row.get("file_data2")),
                    "img3": bool(row.get("file_data3")),
                })

            # Ambil peserta magang yang TIDAK memiliki tugas pada tanggal ini
            cursor.execute("""
                SELECT nama, bidang
                FROM peserta_magang
                WHERE status = 'Sedang Magang'
                AND nama NOT IN (
                    SELECT nama FROM penugasan WHERE DATE(tanggal) = %s
                )
                ORDER BY nama
            """, (tanggal,))
            rows_tanpa_tugas = cursor.fetchall()

            for no, row in enumerate(rows_tanpa_tugas, start=1):
                data_belum_ada_tugas.append({
                    "no": no,
                    "nama": row["nama"],
                    "bidang": row["bidang"],
                })

            # Tambahan setelah bagian data_belum_ada_tugas
            data_progres = []

            # Ambil semua peserta magang aktif
            cursor.execute("""
                SELECT id, nama, bidang, tgl_masuk, tgl_keluar
                FROM peserta_magang
                WHERE status = 'Sedang Magang'
            """)
            peserta_magang = cursor.fetchall()

            for peserta in peserta_magang:
                nama = peserta['nama']
                bidang = peserta['bidang']
                tgl_masuk = peserta['tgl_masuk']
                tgl_keluar = peserta['tgl_keluar']

                # Hitung total hari magang
                total_hari = (tgl_keluar - tgl_masuk).days + 1 if tgl_masuk and tgl_keluar else 0

                # Hitung jumlah tugas yang sudah dikerjakan
                cursor.execute("""
                    SELECT COUNT(*) AS jumlah_tugas
                    FROM penugasan
                    WHERE nama = %s
                """, (nama,))
                jumlah_tugas = cursor.fetchone()['jumlah_tugas'] or 0

                # Hitung persentase progres
                persentase = round((jumlah_tugas / total_hari) * 100, 1) if total_hari > 0 else 0.0

                data_progres.append({
                    'nama': nama,
                    'bidang': bidang,
                    'total_tugas': jumlah_tugas,
                    'total_hari': total_hari,
                    'persentase': persentase
                })


        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return render_template(
            'admin/penugasan_admin.html',
            username=session['username'],
            tanggal=tanggal,
            data=data_penugasan,
            data_belum_ada_tugas=data_belum_ada_tugas,
            data_progres=data_progres  # <-- tambahkan ini
        )

    else:
        flash('Akses khusus admin!', 'danger')
        return redirect(url_for('loginregister'))

@app.route('/img/<int:id_tugas>/<int:ke>')
def img(id_tugas, ke):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT file_data, file_data2, file_data3 FROM penugasan WHERE id_tugas = %s", (id_tugas,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        abort(404)

    # Ambil field file_data sesuai ke
    field_name = f'file_data{"" if ke == 1 else ke}'
    img_data = row.get(field_name)

    if not img_data:
        abort(404)

    # Kirim data gambar, ganti content_type sesuai tipe gambar aslinya (misal image/png)
    return Response(img_data, mimetype='image/jpeg')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
