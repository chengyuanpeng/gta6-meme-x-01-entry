#!/usr/bin/env python3
"""Draw the deterministic make.fun / GTA VI bounty meme using Pillow."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1600, 1200


def gradient():
    im = Image.new('RGB', (W, H))
    p = im.load()
    stops = [(0.0, (27, 17, 66)), (0.43, (157, 38, 122)), (0.72, (241, 103, 83)), (1.0, (255, 174, 91))]
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                a, ca = stops[i]; b, cb = stops[i + 1]
                f = (t - a) / (b - a)
                col = tuple(round(ca[k] * (1-f) + cb[k] * f) for k in range(3))
                break
        for x in range(W):
            p[x, y] = col
    return im


def palm(draw, x, base, height, lean, flip=1):
    ink = (18, 15, 31)
    topx = x + lean
    cy = base-height
    # Slightly bowed trunk, narrowing toward the crown.
    pts = []
    for i in range(25):
        t = i / 24
        yy = base - height*t
        center = x + lean*t + 13*(t*(1-t))
        half = 19*(1-t) + 7*t
        pts.append((center-half, yy))
    for i in range(24, -1, -1):
        t = i / 24
        yy = base - height*t
        center = x + lean*t + 13*(t*(1-t))
        half = 19*(1-t) + 7*t
        pts.append((center+half, yy))
    draw.polygon(pts, fill=ink)
    # Seven broad, tapered fronds. Each leaf follows an arch that rises first,
    # then drops to a tip below the crown; the return edge gives it real area.
    fronds = [(-1, 5, 285, 88), (-1, 18, 260, 104), (-1, 32, 235, 112),
              (-1, 48, 205, 96), (1, 8, 295, 84), (1, 27, 245, 108),
              (1, 46, 215, 100)]
    for side, angle, length, drop in fronds:
        import math
        a = math.radians(angle)
        ex = topx + side * math.cos(a) * length * flip
        ey = cy + drop
        # Place the quadratic control well above the crown to make the frond
        # visibly lift before its downward-curving, low-hanging tip.
        cx = topx + side * math.cos(a) * length * 0.48 * flip
        qy = cy - (115 + drop * 0.42)
        upper, lower = [], []
        for i in range(25):
            t = i / 24
            u = 1 - t
            px = u*u*topx + 2*u*t*cx + t*t*ex
            py = u*u*cy + 2*u*t*qy + t*t*ey
            dx = 2*u*(cx-topx) + 2*t*(ex-cx)
            dy = 2*u*(qy-cy) + 2*t*(ey-qy)
            norm = max(1, math.hypot(dx, dy))
            half_width = 7 * (1-t) ** 0.9
            nx, ny = -dy/norm, dx/norm
            upper.append((px + nx*half_width, py + ny*half_width))
            lower.append((px - nx*half_width, py - ny*half_width))
        draw.polygon(upper + lower[::-1], fill=ink)
    # Two coconuts just below the crown.
    draw.ellipse((topx-12,cy+8,topx-1,cy+19), fill=ink)
    draw.ellipse((topx+3,cy+7,topx+14,cy+18), fill=ink)


def fit_font(text, max_width, start, stroke=0):
    size = start
    while size > 10:
        f = ImageFont.truetype('assets/Anton-Regular.ttf', size)
        box = f.getbbox(text, stroke_width=stroke)
        if box[2]-box[0] <= max_width:
            return f
        size -= 2
    return ImageFont.truetype('assets/Anton-Regular.ttf', size)


def centered_text(draw, text, y, size, maxw, stroke=9):
    f = fit_font(text, maxw, size, stroke)
    box = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
    x = (W - (box[2]-box[0])) // 2 - box[0]
    draw.text((x, y), text, font=f, fill=(255,255,255), stroke_width=stroke, stroke_fill=(11,9,22))


def main():
    im = gradient().convert('RGBA')
    # Subtle atmospheric banding near the horizon.
    haze = Image.new('RGBA', (W,H), (0,0,0,0)); hd = ImageDraw.Draw(haze)
    for n, alpha in enumerate((25,18,12,8)):
        hd.rectangle((0, 675+n*30, W, 695+n*30), fill=(255,185,150,alpha))
    im = Image.alpha_composite(im, haze)
    d = ImageDraw.Draw(im)
    # distant skyline silhouettes
    for x,y,w,h in [(0,635,90,65),(78,600,58,100),(130,628,106,72),(1230,618,95,82),(1320,590,70,110),(1390,630,130,70),(1510,610,90,90)]:
        d.rectangle((x,y,x+w,y+h), fill=(54,25,61,190))
    # Sun disk and clean horizontal slice gaps
    sunbox=(475,410,1125,1060)
    d.ellipse(sunbox, fill=(255,184,86,255))
    for yy, gap in [(570,13),(602,19),(640,27),(681,36)]:
        # Use the local sky hue as a cut through the lower sun.
        sky = (241, 103, 83) if yy >= 864 else ((157, 38, 122) if yy >= 516 else (27, 17, 66))
        d.rectangle((475, yy, 1125, yy+gap), fill=(*sky,255))
    # sea / wet reflective foreground
    d.rectangle((0,690,W,1200), fill=(44,31,70,165))
    d.rectangle((0,690,W,708), fill=(255,186,130,210))
    # reflection streaks, clipped naturally into lower field
    for x,y,w,alpha in [(80,744,250,90),(370,770,320,70),(1010,730,390,85),(40,855,340,55),(490,905,260,62),(1100,940,430,58),(230,1040,330,40),(790,1080,500,42)]:
        d.rounded_rectangle((x,y,x+w,y+7), radius=3, fill=(255,171,135,alpha))
    # sand sheen foreground
    d.rectangle((0,1110,W,1200), fill=(28,22,48,110))
    for x,y,w in [(90,1130,220),(490,1160,300),(1000,1127,260),(1300,1170,220)]:
        d.line((x,y,x+w,y), fill=(246,151,128,70), width=3)
    palm(d, 120, 835, 480, 65, 1)
    palm(d, 1510, 785, 415, -45, -1)
    # neon sign to the left of mascot
    d.polygon([(225,570),(465,570),(465,760),(225,760)], fill=(20,15,38,245), outline=(255,81,190,255), width=6)
    d.rectangle((330,760,357,1010), fill=(17,14,29,255))
    glow = Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    neon_font=ImageFont.truetype('assets/Anton-Regular.ttf',64)
    sign_text='make.fun'
    text_box=gd.textbbox((0,0),sign_text,font=neon_font,stroke_width=2)
    tx=345-(text_box[2]-text_box[0])//2-text_box[0]  # centered in the sign
    gd.text((tx,616),sign_text,font=neon_font,fill=(255,50,188,255),stroke_width=2,stroke_fill=(255,126,220,255))
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(19)))
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(7)))
    d=ImageDraw.Draw(im)
    d.polygon([(225,570),(465,570),(465,760),(225,760)], fill=(20,15,38,245), outline=(255,101,206,255), width=5)
    d.text((tx,616),sign_text,font=neon_font,fill=(255,105,211),stroke_width=2,stroke_fill=(255,195,237))
    # Character, with a soft contact shadow and a compressed, faded reflection.
    badge=Image.open('assets/mark-1024.png').convert('RGBA')
    bh=580; bw=round(badge.width*bh/badge.height)
    badge=badge.resize((bw,bh),Image.Resampling.LANCZOS)
    bx, by = 870, 400
    shadow=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shadow)
    sd.ellipse((bx+55,by+bh-2,bx+bw-35,by+bh+54),fill=(12,7,24,145))
    im=Image.alpha_composite(im,shadow.filter(ImageFilter.GaussianBlur(22)))
    # reflection: flip, compress vertically, fade alpha, soften horizontally
    refl=badge.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    refl=refl.resize((bw,203),Image.Resampling.LANCZOS)
    alpha=refl.getchannel('A').point(lambda v: int(v*0.35))
    refl.putalpha(alpha)
    refl=refl.filter(ImageFilter.GaussianBlur((5,2)))
    im.alpha_composite(refl,(bx+4,by+bh+2))
    # Broken horizontal ripples interrupt the reflected disk.
    ripple=Image.new('RGBA',(W,H),(0,0,0,0)); rd=ImageDraw.Draw(ripple)
    for j,(off,yy,ww) in enumerate([(-30,1000,180),(38,1043,260),(-10,1092,210)]):
        rd.line((bx+bw//2+off-ww//2,yy,bx+bw//2+off+ww//2,yy),fill=(255,190,164,75),width=3)
    im=Image.alpha_composite(im,ripple)
    im.alpha_composite(badge,(bx,by))
    # high contrast typography over sky; generous safe margins
    d=ImageDraw.Draw(im)
    centered_text(d,'WE GOT AI AGENTS',48,130,1450,10)
    centered_text(d,'WINNING REAL BOUNTIES',184,118,1500,10)
    centered_text(d,'BEFORE GTA VI',1000,145,1480,12)
    im.convert('RGB').save('meme.png',format='PNG',optimize=False)
    im.convert('RGB').save('meme.jpg',format='JPEG',quality=90,subsampling=0)


if __name__ == '__main__':
    main()
