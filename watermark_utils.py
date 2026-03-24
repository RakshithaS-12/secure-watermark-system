import cv2
import hashlib

# Generate SHA256 hash
def generate_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path,"rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sha256.update(data)

    return sha256.hexdigest()


# Embed watermark using LSB
def embed_watermark(image_path, watermark_text, output_path):

    img = cv2.imread(image_path)

    binary_watermark = ''.join(format(ord(i),'08b') for i in watermark_text)

    data_index = 0

    for row in img:
        for pixel in row:

            for n in range(3):

                if data_index < len(binary_watermark):

                    pixel[n] = int(format(pixel[n],'08b')[:-1] + binary_watermark[data_index],2)

                    data_index += 1

    cv2.imwrite(output_path,img)