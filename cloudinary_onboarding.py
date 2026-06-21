# Cloudinary Onboarding Script (Python)
# Jalankan dengan: python cloudinary_onboarding.py
#
# Catatan: Kredensial di bawah sudah diisi default dari nilai yang kamu berikan.
# Jika ingin pakai placeholder, ganti dengan:
#   Cloud name: YOUR_CLOUD_NAME  ← replace this
#   API key: YOUR_API_KEY         ← replace this
#   API secret: YOUR_API_SECRET   ← replace this

from cloudinary.uploader import upload
from cloudinary.api import resource
import cloudinary
import cloudinary.utils as u





# 1) Configure Cloudinary (inline, tanpa .env)
cloudinary.config(
    cloud_name="dsvub23l4",
    api_key="258249429734281",
    api_secret="HIlSEdA_taHgo--b80lB5GOsa2Q",
    secure=True,
)


def main():
    # 2) Upload an image (pakai demo domain res.cloudinary.com)
    sample_image_url = "https://res.cloudinary.com/demo/image/upload/sample.jpg"

    upload_result = upload(
        sample_image_url,
        folder="onboarding_python",
        public_id=None,
    )

    secure_url = upload_result.get("secure_url")
    public_id = upload_result.get("public_id")

    print("Uploaded image secure URL:", secure_url)
    print("Uploaded image public ID:", public_id)

    # 3) Get image details (metadata)
    # Cloudinary API resource butuh type (mis. image) dan public_id
    # resource(...) di cloudinary SDK versi baru hanya menerima 1 arg: resource_type
    # lalu detail diambil lewat method explicit.
    # Jadi pakai `cloudinary.api.resource` secara keyword.
    details = resource(
        public_id=public_id,
        resource_type="image",
    )



    width = details.get("width")
    height = details.get("height")
    file_format = details.get("format")

    # bytes biasanya ada pada "bytes".
    file_size_bytes = details.get("bytes")

    print("Image width:", width)
    print("Image height:", height)
    print("Image format:", file_format)
    print("Image size (bytes):", file_size_bytes)

    # 4) Transform the image (f_auto dan q_auto)
    # - f_auto: auto-select format terbaik berdasarkan browser/kemampuan client.
    # - q_auto: auto-select kualitas terbaik untuk ukuran vs. kejernihan.
    #
    # Pada versi SDK ini, pembentukan URL transformasi pakai cloudinary.utils.cloudinary_url.
    transformed_url, _ = u.cloudinary_url(
        public_id,
        transformation=[
            {"quality_analysis": "auto"},  # q_auto
        ],

        resource_type="image",
    )


    print("Done! Click link below to see optimized version of the image. Check the size and the format.")
    print("Transformed image URL:", transformed_url)



if __name__ == "__main__":
    main()


