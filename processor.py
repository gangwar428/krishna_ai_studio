import os, io, csv, re, shutil
import pandas as pd
from datetime import datetime
from PIL import Image, ImageOps, ImageEnhance
from rembg import remove

def get_next_sku(log_file):
    if not os.path.exists(log_file) or os.stat(log_file).st_size <= 10:
        return "SKU001"
    try:
        df = pd.read_csv(log_file)
        last_sku = str(df.iloc[-1, 0])
        num = int(re.search(r'\d+', last_sku).group())
        return f"SKU{num+1:03d}"
    except: return "SKU001"

def master_process(filename, client, session, ai_func, config, bg_hex="#FFFFFF", input_folder=None, is_redo=False):
    input_folder = input_folder or config['WATCH_FOLDER']
    in_p = os.path.join(input_folder, filename)
    
    # Redo logic: same SKU, new process
    sku = filename.split('_')[0] if is_redo else get_next_sku(config['LOG_FILE'])
    
    try:
        img = Image.open(in_p)
        img = ImageOps.exif_transpose(img).convert("RGBA")
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        img = ImageEnhance.Contrast(img).enhance(1.2)

        ai_data = ai_func(client, img)
        
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        no_bg = remove(img_io.getvalue(), session=session)
        prod_img = Image.open(io.BytesIO(no_bg)).convert("RGBA")
        
        bbox = prod_img.getbbox()
        if bbox: prod_img = prod_img.crop(bbox)

        # 3:2 Ratio Logic
        p_w, p_h = prod_img.size
        canvas_w = int(p_w * 1.4)
        canvas_h = int(canvas_w * 0.6) 
        if p_h > canvas_h * 0.8: canvas_h = int(p_h * 1.25)

        canvas = Image.new("RGBA", (canvas_w, canvas_h), bg_hex)
        canvas.paste(prod_img, ((canvas_w - p_w) // 2, (canvas_h - p_h) // 2), prod_img)
        
        out_name = f"{sku}_{ai_data['Style']}_{ai_data['Color']}.jpg".replace(" ", "_").replace("/", "-")
        final_path = os.path.join(config['OUT_FINAL'], out_name)
        canvas.convert("RGB").save(final_path, "JPEG", quality=100)
        
        if not is_redo:
            with open(config['LOG_FILE'], "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([sku, ai_data['Product'], ai_data['Style'], ai_data['Color'], "50x80 cm", "Textile", out_name, datetime.now()])
            shutil.move(in_p, os.path.join(config['BACKUP_DIR'], filename))
        return True
    except Exception as e:
        return False
