import os
import subprocess


def convert_m4a_to_wav(input_directory, output_directory):
    try:
        os.makedirs(output_directory, exist_ok=True)
        files = os.listdir(input_directory)
        for file_name in files:
            if file_name.endswith(".wav"):
                input_file = os.path.join(input_directory, file_name)
                output_file_name = os.path.splitext(file_name)[0] + ".wav"
                output_file = os.path.join(output_directory, output_file_name)
                command = [
                    "ffmpeg",
                    "-y",  
                    "-i", input_file,  
                    "-ar", "16000", 
                    "-ac", "1",  
                    "-b:a", "256k", 
                    output_file 
                ]
                subprocess.run(command, check=True)
                print(f"Dönüştürüldü: {input_file} -> {output_file}")
        print("Tüm dosyalar başarıyla dönüştürüldü!")
    except Exception as e:
        print(f"Hata oluştu: {e}")

input_directory = "kayit"
output_directory = "data/test"
convert_m4a_to_wav(input_directory, output_directory)
