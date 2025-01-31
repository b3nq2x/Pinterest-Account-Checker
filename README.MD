<code>git clone https://github.com/b3nq2x/Pinterest-Account-Checker.git</code>
<h3>INSTALL :</h3>
pip install pandas numpy playwright<br>
playwright install
<br><br>
1. Buat file 1 file cookie menggunakan <a href="https://github.com/b3nq2x/Pinterest-Login">Pinterest Login</a><br>
2. Paste file cookie ke folder <b>\Pinterest Account Checker</b>
<br>
<br>
🔥 Input link profil yang akan di cek pada kolom <b>Profile</b>
<img src="https://blogger.googleusercontent.com/img/a/AVvXsEhNwuwkFXAL0_4Ire3LxCXJ_3PwN_mn9UYgrRpt7HztZpbt7IpzAjsdGVRN7rdArPN8VMCaMeJ9-Bat0EJxO_wk73xNEpEauhxb-77nG583jaDxQ17DNgAzKOEYjzhdGNinQFa_SwMMjCv4SYH3a1V4h06uKquXUhG-miyHzoEYTqfj2yr21LQ8Cqtq3och"/>
<br><br><br>
🔥 <b>cekindexing.py</b> untuk mengetahui apakah akun sudah terindex atau belum<br>
- Jika pada kolom Indexing tercatat <b>False</b> maka akun belum terindex<br>
- Jika pada kolom Indexing tercatat <b>True</b> maka akun sudah terindex<br>
- Jika pada kolom Indexing tercatat <b>Deactive</b> maka status akun suspended<br>
<br>
<img src="https://blogger.googleusercontent.com/img/a/AVvXsEjQI35vmY36ScBg2aLeXa91vvXPxb3sCaFIXUYbmTgvKHcJqvbg3cadKnIBZgb-3dF0gXTVLR0JtgNONhNz3i6CSYCXe0sMMo4I_VQFZEYmTB-3NC_M9JQpCOABgw9r9v2VsMAnjyMqpAlEGD0850fA-IJPlmEDnAtRl9nm61rHmmuCmFuiuGE1ItYpdg_f"/>
<br><br><br>
🔥 <b>cekall.py</b> untuk mengetahui status Indexed, Jumlah Follower, Jumlah	Following, Jumlah Boards, Jumlah Pins & jumlah Views / month :<br>
- Jika pada kolom Indexing tercatat <b>True</b> maka status akun <b>Aktif</b><br>  
- Jika pada kolom Indexing tercatat <b>Shadow Ban</b> maka status akun <b>Shadow Ban</b><br>  
- Jika pada kolom Indexing tercatat <b>Suspended</b> maka status akun <b>Suspended</b><br>  
<br>
<img src="https://blogger.googleusercontent.com/img/a/AVvXsEj8XkxEwdz1fGLAiUq14cKoG0PBsPtblYiV3Q71zIIvSbAgI6wTPImuMNliJamc2Tq9gZESvopAcBf2if4EN1RgplD15dGcws0BlnRPQ6CCgDDFS2AtmVjE2Zwh1iz4qcrrZODkbFDcRZ2TjtmFc8vZGXk8TM8SHgsOpIMGPLAcgHoG6iTO8mVCuvwlXI0L"/>
<br>
<br>
<b>NOTE : Jangan membuka file status.csv saat script sedang dijalankan</b>