import os
import shutil

def copy_css(source_file):
    source_path = os.path.join('css', f"{source_file}.css")
    
    if not os.path.exists(source_path):
        print(f"Kaynak dosya bulunamadı: {source_path}")
        return

    # Dosya adıyla aynı isme sahip yeni bir dosya oluşturuyoruz
    new_path = f"{source_file}.css"
    
    shutil.copy(source_path, new_path)
    print(f"'{source_file}.css' dosyası başarıyla indirildi!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Kullanım: python trcss.py <dosya_adi>")
    else:
        _, source_file = sys.argv
        copy_css(source_file)