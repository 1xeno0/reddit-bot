from PIL import Image, ImageDraw, ImageFont

def generate_label_image(label_id, title, username="@storiesbyjt", love_count="99+", send_count="99+", save_count="9999+"):
    # === Config ===
    canvas_width, canvas_height = 660, 220
    output_path = f'labels/outputs/{label_id}.png'
    avatar_img_path = 'labels/preset/avatar.png'
    save_img_path = 'labels/preset/save.png'
    love_img_path = 'labels/preset/love.png'
    send_img_path = 'labels/preset/send.png'
    verif_img_path = 'labels/preset/verif.png'
    
    username_font = ImageFont.truetype('labels/preset/bold.otf', 20)
    title_font = ImageFont.truetype('labels/preset/bold.otf', 23)
    small_font = ImageFont.truetype('labels/preset/bold.otf', 15)

    if not username:
        username = '@storiesbyjt'
    if not title:
        title = 'The Craigslist Ad That Shook Me For The Rest Of My Life...'
    
    # === Create white canvas ===
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(canvas)

    # === Load and paste the avatar image ===
    avatar_img = Image.open(avatar_img_path).convert("RGBA")
    avatar_img = avatar_img.resize((65, 65))
    canvas.paste(avatar_img, (15, 11), avatar_img)  
    
    # === Draw username text ===
    draw.text((87, 20), username, font=username_font, fill='black', width=1)
    verif_img = Image.open(verif_img_path).convert("RGBA")
    verif_img = verif_img.resize((23, 23))
    bbox = draw.textbbox((0, 0), username, font=username_font)
    text_width = bbox[2] - bbox[0]
    canvas.paste(verif_img, (87 + text_width + 2, 22), verif_img)   
    
    # === Draw title text ===
    draw.text((25, 100), title, font=title_font, fill='black')
    
    # === Draw love and count text ===
    love_img = Image.open(love_img_path).convert("RGBA")
    love_img = love_img.resize((27, 27))
    canvas.paste(love_img, (25, 175), love_img)
    draw.text((58, 180), "99+", font=small_font, fill='#969696')
    
    # === Draw send and count text ===
    send_img = Image.open(send_img_path).convert("RGBA")
    send_img = send_img.resize((27, 27))
    canvas.paste(send_img, (96, 175), send_img)
    draw.text((128, 180), "99+", font=small_font, fill='#969696', width=1)
    
    # === Draw save and count text ===
    save_img = Image.open(save_img_path).convert("RGBA")
    save_img = save_img.resize((20, 20))
    canvas.paste(save_img, (88, 46), save_img)
    draw.text((112, 47), "9999+", font=small_font, fill='#969696')
    
    # === Save the final image ===
    canvas.save(output_path)
    
    print(f"✅ Saved as {output_path}")
    
    
if __name__ == "__main__":
    generate_label_image(1, "@storiesbyjt", "The Craigslist Ad That Shook Me For The Rest Of My Life...")
    
    