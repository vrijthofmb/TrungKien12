from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os
import base64

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


# ==========================================
# MỞ WEBSITE
# ==========================================

@app.route("/")
def home():
    return send_from_directory(
        app.root_path,
        "index.html"
    )


@app.route("/<path:path>")
def files(path):
    return send_from_directory(
        app.root_path,
        path
    )


# ==========================================
# AI CHAT
# ==========================================

@app.route(
    "/api/ai",
    methods=["POST"]
)
def ai():

    data = request.json or {}

    question = data.get(
        "message",
        ""
    )

    history = data.get(
        "history",
        []
    )

    library = data.get(
        "library",
        []
    )


    # --------------------------------------
    # LẤY DỮ LIỆU KHO HỌC TẬP
    # --------------------------------------

    library_text = ""

    for item in library:

        library_text += f"""

Môn học: {item.get('subject')}

Loại: {item.get('type')}

Tiêu đề: {item.get('title')}

Nội dung:
{item.get('body')}

"""


    # --------------------------------------
    # CẤU HÌNH AI
    # --------------------------------------

    system = """

Bạn là AI Học Tập của website
Kho Học Tập.

Bạn phải trả lời bằng tiếng Việt.

Hãy giải thích dễ hiểu,
đặc biệt khi người dùng là người mới học.

Bạn có thể:

- giải bài tập
- phân tích đề
- giải thích kiến thức
- phân tích dữ liệu
- hỗ trợ lập trình
- tìm thông tin trong kho học tập

Nếu câu hỏi liên quan đến dữ liệu
trong kho học tập thì ưu tiên sử dụng
dữ liệu đó.

Không được tự bịa nội dung tài liệu.

Nếu không tìm thấy thông tin trong kho,
hãy nói rõ rằng thông tin đó không có
trong kho.

Dữ liệu trong kho học tập:

""" + library_text


    # --------------------------------------
    # TẠO LỊCH SỬ CHAT
    # --------------------------------------

    messages = [
        {
            "role": "system",
            "content": system
        }
    ]


    for item in history[-10:]:
        messages.append(item)


    messages.append({
        "role": "user",
        "content": question
    })


    # --------------------------------------
    # GỌI AI
    # --------------------------------------

    try:

        response = client.responses.create(
            model="gpt-5",
            input=messages
        )

        return jsonify({
            "answer": response.output_text
        })


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ==========================================
# AI PHÂN TÍCH ẢNH
# ==========================================

@app.route(
    "/api/ai-image",
    methods=["POST"]
)
def ai_image():

    image = request.files.get("image")


    if not image:

        return jsonify({
            "error": "Không nhận được ảnh."
        }), 400


    # --------------------------------------
    # ĐỌC ẢNH
    # --------------------------------------

    image_data = base64.b64encode(
        image.read()
    ).decode("utf-8")

    mime_type = image.mimetype


    # --------------------------------------
    # GỬI ẢNH CHO AI
    # --------------------------------------

    try:

        response = client.responses.create(

            model="gpt-5",

            input=[

                {
                    "role": "user",

                    "content": [

                        {
                            "type": "input_text",

                            "text": """

Hãy đọc ảnh này và phân tích
nội dung bằng tiếng Việt.

Nếu là bài tập:

- Đọc đề
- Xác định yêu cầu
- Giải thích cách làm
- Đưa lời giải nếu có thể

Nếu là biểu đồ hoặc dữ liệu:

- Phân tích các thông tin quan trọng
- Nêu các số liệu đáng chú ý
- Giải thích kết quả dễ hiểu

Nếu ảnh không phải bài tập,
hãy mô tả những gì nhìn thấy
và giải thích thông tin quan trọng.

Hãy trình bày rõ ràng, dễ hiểu
và bằng tiếng Việt.
"""
                        },

                        {
                            "type": "input_image",

                            "image_url":
                                f"data:{mime_type};base64,{image_data}"
                        }

                    ]
                }

            ]
        )


        return jsonify({

            "answer":
                response.output_text

        })


    except Exception as e:

        return jsonify({

            "error":
                str(e)

        }), 500


# ==========================================
# CHẠY SERVER
# ==========================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )