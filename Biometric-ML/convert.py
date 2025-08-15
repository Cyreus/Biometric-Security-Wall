import os
import subprocess


def convert_m4a_to_wav(input_directory, output_directory):
    try:
        # Çıktı klasörünü oluştur
        os.makedirs(output_directory, exist_ok=True)

        # Klasördeki tüm dosyaları listele
        files = os.listdir(input_directory)

        for file_name in files:
            # Sadece ".m4a" uzantılı dosyaları seç
            if file_name.endswith(".wav"):
                input_file = os.path.join(input_directory, file_name)

                # Yeni dosya adını .wav formatında oluştur
                output_file_name = os.path.splitext(file_name)[0] + ".wav"
                output_file = os.path.join(output_directory, output_file_name)

                # FFmpeg komutu
                command = [
                    "ffmpeg",
                    "-y",  # Mevcut dosyayı üzerine yaz
                    "-i", input_file,  # Girdi dosyası
                    "-ar", "16000",  # 16kHz örnekleme oranı
                    "-ac", "1",  # Mono kanal
                    "-b:a", "256k",  # 128kbps bit hızı
                    output_file  # Çıktı dosyası
                ]

                # FFmpeg'i çalıştır
                subprocess.run(command, check=True)
                print(f"Dönüştürüldü: {input_file} -> {output_file}")

        print("Tüm dosyalar başarıyla dönüştürüldü!")

    except Exception as e:
        print(f"Hata oluştu: {e}")


# Kullanıcıdan klasör yollarını al
input_directory = "kayit"
output_directory = "data/test"

# Fonksiyonu çağır
convert_m4a_to_wav(input_directory, output_directory)
