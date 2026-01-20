from PIL import Image, ImageDraw, ImageFont
import os

# 创建一个256x256的图标
icon_size = (256, 256)
icon = Image.new('RGBA', icon_size, (255, 255, 255, 0))
draw = ImageDraw.Draw(icon)

# 绘制背景矩形
draw.rectangle([(0, 0), icon_size], fill=(74, 122, 188))

# 绘制下载图标
# 外框
draw.rectangle([(80, 120), (120, 180)], fill=(255, 255, 255))
# 下载箭头
draw.polygon([(100, 100), (80, 120), (120, 120)], fill=(255, 255, 255))

# 绘制GB文字
font = ImageFont.truetype('arial.ttf', 72)
gb_text = 'GB'
text_bbox = draw.textbbox((0, 0), gb_text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]
text_x = (icon_size[0] - text_width) / 2
text_y = (icon_size[1] - text_height) / 2 - 10
draw.text((text_x, text_y), gb_text, font=font, fill=(255, 255, 255))

# 保存图标
icon_path = 'gb_downloader.ico'
icon.save(icon_path)
print(f"图标已保存到: {os.path.abspath(icon_path)}")
