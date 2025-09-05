import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin

def sanitize_name(name):
    """
    Membersihkan nama, mengubahnya menjadi huruf kecil, 
    dan mengganti spasi dengan tanda hubung (-).
    Contoh: "Manchester Utd" -> "manchester-utd"
    """
    # 1. Hapus karakter yang tidak valid, sisakan huruf, angka, dan spasi
    cleaned_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c.isspace()]).strip()
    
    # 2. Ganti spasi dengan hyphen dan ubah ke huruf kecil
    return cleaned_name.replace(' ', '-').lower()

def download_logos(league_urls, output_folder="Logos"):
    """
    Menggunakan Selenium untuk mengunduh logo tim dari berbagai liga ke dalam
    satu folder, menggunakan hyphen untuk nama file, dan menghindari duplikasi.
    """
    # -- Pengaturan Otomatis untuk Selenium WebDriver --
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"Error saat inisialisasi WebDriver: {e}")
        print("Pastikan Google Chrome sudah terinstal di sistem Anda.")
        return

    # Buat Folder Tujuan
    os.makedirs(output_folder, exist_ok=True)
    print(f"Folder output '{output_folder}' telah disiapkan.")
    
    base_url = "https://www.flashscore.com"
    wait = WebDriverWait(driver, 20)

    # -- Memproses Setiap URL Liga --
    for url in league_urls:
        try:
            print(f"\n{'='*20}\nMembaca daftar tim dari: {url}\n{'='*20}")
            driver.get(url)

            # Dapatkan Semua Link Halaman Tim
            team_elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.tableCellParticipant__image'))
            )
            team_urls = [urljoin(base_url, el.get_attribute('href')) for el in team_elements]
            print(f"Ditemukan {len(team_urls)} tim.")

            # Kunjungi Setiap Halaman Tim
            for i, team_url in enumerate(team_urls, 1):
                try:
                    driver.get(team_url)
                    
                    logo_element = wait.until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'img.heading__logo'))
                    )
                    
                    logo_url = logo_element.get_attribute('src')
                    
                    # --- PERUBAHAN DI SINI ---
                    # Nama tim sekarang akan diproses oleh fungsi sanitize_name yang baru
                    team_name = sanitize_name(logo_element.get_attribute('alt'))
                    
                    file_extension = os.path.splitext(logo_url)[1] or '.png'
                    file_name = f"{team_name}{file_extension}"
                    file_path = os.path.join(output_folder, file_name)

                    # Cek Duplikasi
                    if os.path.exists(file_path):
                        print(f"  ({i}/{len(team_urls)}) Logo '{file_name}' sudah ada. Melewati...")
                        continue
                    
                    # Unduh gambar jika belum ada
                    response = requests.get(logo_url)
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"  ({i}/{len(team_urls)}) BERHASIL diunduh: '{file_name}'")
                
                except Exception as e:
                    print(f"  -> Gagal memproses tim di URL {team_url}. Error: {e}")
            
        except Exception as e:
            print(f"Gagal memproses URL liga {url}. Error: {e}")
            
    driver.quit()
    print(f"\n{'='*20}\nSkrip Selesai. Semua logo tersimpan di folder '{output_folder}'.\n{'='*20}")

# -- Program Utama --
if __name__ == "__main__":
    # --- DAFTAR URL LIGA YANG INGIN DIUNDUH ---
    # Cukup tambahkan URL klasemen liga lain dari Flashscore di sini
    urls_to_scrape = [
        #"https://www.flashscore.com/football/england/premier-league/standings/#/OEEq9Yvp/table/overall",
        #"https://www.flashscore.com/football/france/ligue-1/standings/#/j9QeTLPP/table/overall",
        #"https://www.flashscore.com/football/germany/bundesliga/standings/#/8UYeqfiD/table/overall",
        #"https://www.flashscore.com/football/italy/serie-a/standings/#/6PWwAsA7/table/overall",
        #"https://www.flashscore.com/football/netherlands/eredivisie/standings/#/dWKtjvdd/table/overall",
        #"https://www.flashscore.com/football/spain/laliga/standings/#/vcm2MhGk/table/overall",
        #"https://www.flashscore.com/football/europe/champions-league/standings/#/UiRZST3U/table/overall"
        "https://www.flashscore.com/football/europe/world-championship/standings/#/jV1yMmNl/table/overall",
        "https://www.flashscore.com/football/europe/world-championship/standings/#/xASUZ6il/table/overall",
        "https://www.flashscore.com/football/europe/world-championship/standings/#/OIEnt9EK/table/overall"
    ]
    
    download_logos(urls_to_scrape)