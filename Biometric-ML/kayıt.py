import os

def rename_files_in_directory(directory, start_number):
    try:
        # Klasördeki tüm dosyaları listele
        files = os.listdir(directory)
        files.sort()  # Dosya sıralamasını garanti etmek için

        # Dosyaları yeniden adlandır
        current_number = start_number
        for i, file_name in enumerate(files):
            # Yalnızca ".wav" uzantılı dosyaları seç
            if file_name.endswith(".wav"):
                old_path = os.path.join(directory, file_name)
                new_name = f"{current_number}.wav"
                new_path = os.path.join(directory, new_name)

                os.rename(old_path, new_path)
                print(f"{old_path} -> {new_path}")

                current_number += 1

        print("Dosya yeniden adlandırma işlemi tamamlandı!")
    except Exception as e:
        print(f"Hata oluştu: {e}")


# Fonksiyonu çağır
rename_files_in_directory("kayit",72)
