
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Frontend: HTML + CSS
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Online Shopping Bill Calculator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #dbeafe, #ede9fe);
            margin: 0;
            padding: 30px 15px;
        }

        .container {
            background: white;
            max-width: 420px;
            margin: 30px auto;
            padding: 30px;
            border-radius: 18px;
            box-shadow: 0 8px 25px #00000020;
        }

        h1 {
            text-align: center;
            color: #4f46e5;
            font-size: 25px;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-top: 15px;
            font-weight: bold;
            color: #333;
        }

        input {
            width: 100%;
            padding: 12px;
            margin-top: 7px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 15px;
        }

        input:focus {
            outline: 2px solid #818cf8;
            border-color: #4f46e5;
        }

        button {
            width: 100%;
            padding: 13px;
            margin-top: 22px;
            background: #4f46e5;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            background: #3730a3;
        }

        #result {
            display: none;
            margin-top: 25px;
            padding: 18px;
            background: #eefcf3;
            border-radius: 10px;
            color: #166534;
            line-height: 2;
            overflow-wrap: anywhere;
        }

        .final {
            font-size: 20px;
            font-weight: bold;
            border-top: 1px solid #bbf7d0;
            padding-top: 10px;
        }

        #message {
            color: #dc2626;
            margin-top: 15px;
            text-align: center;
        }

        footer {
            text-align: center;
            color: #666;
            font-size: 13px;
            margin-top: 20px;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>🛍️ Shopping Bill</h1>
        <p class="subtitle">Calculate your shopping bill easily</p>

        <form id="billForm">
            <label for="name">Customer Name</label>
            <input id="name" type="text"
                   placeholder="Enter your name" required>

            <label for="product">Product Name</label>
            <input id="product" type="text"
                   placeholder="Enter product name" required>

            <label for="price">Price per Item (₹)</label>
            <input id="price" type="number"
                   placeholder="Enter price" min="0.01"
                   step="0.01" required>

            <label for="quantity">Quantity</label>
            <input id="quantity" type="number"
                   placeholder="Enter quantity" min="1"
                   step="1" required>

            <button type="submit">Calculate Bill</button>
        </form>

        <p id="message" role="alert"></p>

        <div id="result" aria-live="polite">
            <h3>🧾 Your Bill</h3>
            <div id="billDetails"></div>
        </div>

        <footer>Thank you for shopping with us!</footer>
    </div>

    <script>
        const form = document.getElementById("billForm");

        form.addEventListener("submit", async function(event) {
            event.preventDefault();

            const message = document.getElementById("message");
            const result = document.getElementById("result");
            const details = document.getElementById("billDetails");

            message.textContent = "";
            result.style.display = "none";

            const customerName = document.getElementById("name").value.trim();
            const productName = document.getElementById("product").value.trim();
            const price = Number(document.getElementById("price").value);
            const quantity = Number(document.getElementById("quantity").value);

            if (!customerName || !productName ||
                !Number.isFinite(price) || price <= 0 ||
                !Number.isInteger(quantity) || quantity <= 0) {
                message.textContent = "Please enter valid details.";
                return;
            }

            try {
                const response = await fetch("/calculate", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        name: customerName,
                        product: productName,
                        price: price,
                        quantity: quantity
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    message.textContent = data.error || "Calculation failed.";
                    return;
                }

                details.replaceChildren();

                function addLine(label, value, className = "") {
                    const line = document.createElement("div");
                    line.textContent = label + ": " + value;
                    if (className) line.className = className;
                    details.appendChild(line);
                }

                addLine("Customer", data.name);
                addLine("Product", data.product);
                addLine("Price per item", "₹" + data.price.toFixed(2));
                addLine("Quantity", data.quantity);
                addLine("Total amount", "₹" + data.total.toFixed(2));
                addLine("Discount (10%)", "₹" + data.discount.toFixed(2));
                addLine("Final bill", "₹" + data.final_bill.toFixed(2), "final");

                result.style.display = "block";

            } catch (error) {
                message.textContent =
                    "Cannot connect to the server. Please try again.";
            }
        });
    </script>
</body>
</html>
"""

# Show the frontend
@app.route("/")
def home():
    return render_template_string(HTML)


# Calculate the shopping bill
@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Please enter the details."}), 400

        name = str(data.get("name", "")).strip()
        product = str(data.get("product", "")).strip()
        price = float(data.get("price", 0))
        quantity = int(data.get("quantity", 0))

        if not name or not product:
            return jsonify({"error": "Name and product are required."}), 400

        if price <= 0 or quantity <= 0:
            return jsonify({"error": "Price and quantity must be positive."}), 400

        total = round(price * quantity, 2)
        discount = round(total * 0.10, 2)
        final_bill = round(total - discount, 2)

        return jsonify({
            "name": name,
            "product": product,
            "price": price,
            "quantity": quantity,
            "total": total,
            "discount": discount,
            "final_bill": final_bill
        })

    except (ValueError, TypeError):
        return jsonify({"error": "Please enter valid price and quantity."}), 400


if __name__ == "__main__":
    app.run(debug=True)