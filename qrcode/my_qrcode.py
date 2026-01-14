import argparse
import qrcode

def generate_qr(data, output_file):
    qr = qrcode.QRCode(
        version=1,  # controls size: 1 = 21x21, higher = larger
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,  # size of each box in pixels
        border=4,     # quiet zone (recommended minimum is 4)
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_file)

from PIL import Image

def generate_qr_with_logo(
    data,
    output_file,
    logo_path,
    qr_size=500,
    logo_scale=0.2
):
    """
    data        : string to encode
    output_file : output PNG file
    logo_path   : path to JPEG/PNG logo
    qr_size     : final QR image size (px)
    logo_scale  : logo size relative to QR (0.15–0.25 recommended)
    """

    # High error correction is important when adding a logo
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGBA")

    # Resize QR to fixed size
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)

    # Load logo
    logo = Image.open(logo_path).convert("RGBA")

    # Calculate logo size
    logo_size = int(qr_size * logo_scale)
    logo.thumbnail((logo_size, logo_size), Image.LANCZOS)

    # Center position
    x = (qr_img.size[0] - logo.size[0]) // 2
    y = (qr_img.size[1] - logo.size[1]) // 2

    # Optional: white background behind logo for contrast
    padding = 10
    bg_size = (logo.size[0] + padding, logo.size[1] + padding)
    bg = Image.new("RGBA", bg_size, (255, 255, 255, 255))
    bg_x = x - padding // 2
    bg_y = y - padding // 2
    qr_img.paste(bg, (bg_x, bg_y), bg)

    # Paste logo
    qr_img.paste(logo, (x, y), logo)

    qr_img.save(output_file)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='url', required=True)
    parser.add_argument('-f', '--filename', help='filename', required=True)
    parser.add_argument('-l', '--logo', help='Embedded logo', required=False)

    args = parser.parse_args()
    if not args.logo:
        generate_qr(args.url, args.filename)
    else:
        generate_qr_with_logo(
        data=args.url,
        output_file=args.filename,
        logo_path=args.logo,   # JPEG works fine
        logo_scale=0.2
    )

    print(f'QR code created as {args.filename}')

