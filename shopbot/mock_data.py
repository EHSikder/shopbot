"""
Mock database for ShopBot - E-commerce Support Telegram Bot
All data is fictional and for demo purposes only.
"""

# ─────────────────────────────────────────────
# PRODUCTS (60 items across 6 categories)
# ─────────────────────────────────────────────
PRODUCTS = {
    # ── Electronics ──
    1:  {"name": "Wireless Noise-Cancelling Headphones", "price": 89.99,  "category": "Electronics",  "stock": 15, "rating": 4.8, "emoji": "🎧"},
    2:  {"name": "Smart Watch Pro X",                    "price": 149.99, "category": "Electronics",  "stock": 8,  "rating": 4.6, "emoji": "⌚"},
    3:  {"name": "USB-C Fast Charging Hub (7-Port)",     "price": 39.99,  "category": "Electronics",  "stock": 30, "rating": 4.5, "emoji": "🔌"},
    4:  {"name": "Bluetooth Portable Speaker",           "price": 59.99,  "category": "Electronics",  "stock": 20, "rating": 4.7, "emoji": "🔊"},
    5:  {"name": "4K Webcam with Ring Light",            "price": 79.99,  "category": "Electronics",  "stock": 12, "rating": 4.4, "emoji": "📷"},
    6:  {"name": "Mechanical Gaming Keyboard RGB",       "price": 109.99, "category": "Electronics",  "stock": 10, "rating": 4.9, "emoji": "⌨️"},
    7:  {"name": "Wireless Ergonomic Mouse",             "price": 45.99,  "category": "Electronics",  "stock": 25, "rating": 4.5, "emoji": "🖱️"},
    8:  {"name": "27\" Curved Monitor 144Hz",            "price": 299.99, "category": "Electronics",  "stock": 5,  "rating": 4.8, "emoji": "🖥️"},
    9:  {"name": "TWS Earbuds with ANC",                 "price": 69.99,  "category": "Electronics",  "stock": 18, "rating": 4.6, "emoji": "🎵"},
    10: {"name": "10000mAh Power Bank Slim",             "price": 29.99,  "category": "Electronics",  "stock": 40, "rating": 4.3, "emoji": "🔋"},

    # ── Fashion ──
    11: {"name": "Premium Slim-Fit Dress Shirt (White)", "price": 34.99,  "category": "Fashion",      "stock": 50, "rating": 4.4, "emoji": "👔"},
    12: {"name": "Vintage Denim Jacket",                 "price": 69.99,  "category": "Fashion",      "stock": 20, "rating": 4.7, "emoji": "🧥"},
    13: {"name": "Running Sneakers Ultra-Light",         "price": 89.99,  "category": "Fashion",      "stock": 30, "rating": 4.8, "emoji": "👟"},
    14: {"name": "Leather Crossbody Bag",                "price": 54.99,  "category": "Fashion",      "stock": 15, "rating": 4.5, "emoji": "👜"},
    15: {"name": "Classic Aviator Sunglasses",           "price": 24.99,  "category": "Fashion",      "stock": 60, "rating": 4.3, "emoji": "🕶️"},
    16: {"name": "Cozy Oversized Hoodie (Grey)",         "price": 44.99,  "category": "Fashion",      "stock": 35, "rating": 4.6, "emoji": "👕"},
    17: {"name": "Men's Slim Chino Pants",               "price": 39.99,  "category": "Fashion",      "stock": 25, "rating": 4.4, "emoji": "👖"},
    18: {"name": "Women's Floral Summer Dress",          "price": 49.99,  "category": "Fashion",      "stock": 22, "rating": 4.7, "emoji": "👗"},
    19: {"name": "Wool Blend Winter Scarf",              "price": 19.99,  "category": "Fashion",      "stock": 45, "rating": 4.2, "emoji": "🧣"},
    20: {"name": "Genuine Leather Belt (Brown)",         "price": 27.99,  "category": "Fashion",      "stock": 38, "rating": 4.5, "emoji": "🩱"},

    # ── Home & Kitchen ──
    21: {"name": "Air Fryer 5.5L Digital",               "price": 99.99,  "category": "Home",         "stock": 10, "rating": 4.9, "emoji": "🍳"},
    22: {"name": "Smart LED Desk Lamp",                  "price": 39.99,  "category": "Home",         "stock": 20, "rating": 4.5, "emoji": "💡"},
    23: {"name": "Non-Stick Cookware Set (5pcs)",        "price": 79.99,  "category": "Home",         "stock": 12, "rating": 4.6, "emoji": "🥘"},
    24: {"name": "Electric Coffee Grinder",              "price": 34.99,  "category": "Home",         "stock": 18, "rating": 4.4, "emoji": "☕"},
    25: {"name": "Stainless Steel Water Bottle 1L",      "price": 22.99,  "category": "Home",         "stock": 55, "rating": 4.7, "emoji": "🍶"},
    26: {"name": "Cordless Handheld Vacuum",             "price": 59.99,  "category": "Home",         "stock": 14, "rating": 4.5, "emoji": "🧹"},
    27: {"name": "Bamboo Cutting Board Set",             "price": 27.99,  "category": "Home",         "stock": 30, "rating": 4.3, "emoji": "🔪"},
    28: {"name": "Aromatherapy Diffuser 500ml",          "price": 29.99,  "category": "Home",         "stock": 22, "rating": 4.6, "emoji": "🕯️"},
    29: {"name": "Digital Kitchen Scale",                "price": 18.99,  "category": "Home",         "stock": 40, "rating": 4.4, "emoji": "⚖️"},
    30: {"name": "Automatic Plant Watering System",      "price": 44.99,  "category": "Home",         "stock": 9,  "rating": 4.2, "emoji": "🌿"},

    # ── Sports & Fitness ──
    31: {"name": "Adjustable Dumbbell Set 5-30kg",       "price": 189.99, "category": "Sports",       "stock": 7,  "rating": 4.8, "emoji": "🏋️"},
    32: {"name": "Yoga Mat Non-Slip 6mm",                "price": 29.99,  "category": "Sports",       "stock": 40, "rating": 4.6, "emoji": "🧘"},
    33: {"name": "Resistance Band Set (5 levels)",       "price": 19.99,  "category": "Sports",       "stock": 60, "rating": 4.5, "emoji": "💪"},
    34: {"name": "Jump Rope Speed Cable",                "price": 14.99,  "category": "Sports",       "stock": 55, "rating": 4.3, "emoji": "🤸"},
    35: {"name": "Foam Roller Deep Tissue",              "price": 24.99,  "category": "Sports",       "stock": 30, "rating": 4.7, "emoji": "🏃"},
    36: {"name": "Running Belt Waterproof",              "price": 17.99,  "category": "Sports",       "stock": 35, "rating": 4.4, "emoji": "🏅"},
    37: {"name": "Smart Jump Rope with Counter",         "price": 34.99,  "category": "Sports",       "stock": 20, "rating": 4.5, "emoji": "⏱️"},
    38: {"name": "Ab Roller Wheel with Knee Pad",        "price": 22.99,  "category": "Sports",       "stock": 28, "rating": 4.6, "emoji": "🎯"},
    39: {"name": "Sports Water Bottle BPA-Free 750ml",   "price": 15.99,  "category": "Sports",       "stock": 70, "rating": 4.3, "emoji": "💧"},
    40: {"name": "Pull-Up Bar Doorframe (No Drill)",     "price": 39.99,  "category": "Sports",       "stock": 16, "rating": 4.7, "emoji": "🚀"},

    # ── Books & Stationery ──
    41: {"name": "The Lean Startup - Hardcover",         "price": 16.99,  "category": "Books",        "stock": 25, "rating": 4.8, "emoji": "📚"},
    42: {"name": "Productivity Planner 2025 Edition",    "price": 21.99,  "category": "Books",        "stock": 30, "rating": 4.6, "emoji": "📓"},
    43: {"name": "Atomic Habits - Paperback",            "price": 13.99,  "category": "Books",        "stock": 45, "rating": 4.9, "emoji": "📖"},
    44: {"name": "Premium Gel Pen Set (12 colors)",      "price": 11.99,  "category": "Books",        "stock": 60, "rating": 4.4, "emoji": "✒️"},
    45: {"name": "A4 Sketch Pad 200gsm",                 "price": 9.99,   "category": "Books",        "stock": 50, "rating": 4.3, "emoji": "🎨"},
    46: {"name": "Sticky Notes Mega Pack (2000pcs)",     "price": 12.99,  "category": "Books",        "stock": 80, "rating": 4.5, "emoji": "📌"},
    47: {"name": "Leather Journal Handmade",             "price": 24.99,  "category": "Books",        "stock": 18, "rating": 4.7, "emoji": "📔"},
    48: {"name": "Desk Organizer Bamboo 5-Compartment",  "price": 29.99,  "category": "Books",        "stock": 22, "rating": 4.4, "emoji": "🗂️"},
    49: {"name": "Deep Work by Cal Newport",             "price": 14.99,  "category": "Books",        "stock": 35, "rating": 4.8, "emoji": "🧠"},
    50: {"name": "Highlighter Set Pastel (8 colors)",    "price": 7.99,   "category": "Books",        "stock": 90, "rating": 4.3, "emoji": "🖊️"},

    # ── Beauty & Care ──
    51: {"name": "Vitamin C Face Serum 30ml",            "price": 24.99,  "category": "Beauty",       "stock": 28, "rating": 4.7, "emoji": "✨"},
    52: {"name": "Hyaluronic Acid Moisturizer",          "price": 19.99,  "category": "Beauty",       "stock": 32, "rating": 4.5, "emoji": "💆"},
    53: {"name": "Electric Facial Cleanser Brush",       "price": 34.99,  "category": "Beauty",       "stock": 15, "rating": 4.6, "emoji": "🫧"},
    54: {"name": "SPF 50 Sunscreen Lightweight",         "price": 16.99,  "category": "Beauty",       "stock": 50, "rating": 4.4, "emoji": "☀️"},
    55: {"name": "Beard Grooming Kit (8pcs)",            "price": 29.99,  "category": "Beauty",       "stock": 20, "rating": 4.8, "emoji": "🪒"},
    56: {"name": "Rose Water Facial Mist 100ml",         "price": 12.99,  "category": "Beauty",       "stock": 45, "rating": 4.3, "emoji": "🌹"},
    57: {"name": "Argan Oil Hair Serum 50ml",            "price": 17.99,  "category": "Beauty",       "stock": 30, "rating": 4.5, "emoji": "💎"},
    58: {"name": "Charcoal Teeth Whitening Kit",         "price": 21.99,  "category": "Beauty",       "stock": 25, "rating": 4.2, "emoji": "🦷"},
    59: {"name": "Jade Face Roller & Gua Sha Set",       "price": 22.99,  "category": "Beauty",       "stock": 18, "rating": 4.6, "emoji": "💚"},
    60: {"name": "Collagen Eye Patches (60 pairs)",      "price": 14.99,  "category": "Beauty",       "stock": 35, "rating": 4.4, "emoji": "👁️"},
}

# ─────────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────────
CATEGORIES = {
    "Electronics": "💻",
    "Fashion":     "👗",
    "Home":        "🏠",
    "Sports":      "🏋️",
    "Books":       "📚",
    "Beauty":      "✨",
}

# ─────────────────────────────────────────────
# EXISTING ORDERS (for tracking demo)
# ─────────────────────────────────────────────
EXISTING_ORDERS = {
    "ORD-10045": {
        "items": [{"id": 1, "qty": 1}, {"id": 9, "qty": 2}],
        "total": 229.97,
        "status": "Shipped",
        "tracking": "TRK-882341-BD",
        "eta": "March 13, 2026",
        "address": "House 12, Road 5, Dhanmondi, Dhaka",
        "payment": "Card",
    },
    "ORD-10032": {
        "items": [{"id": 21, "qty": 1}],
        "total": 99.99,
        "status": "Delivered",
        "tracking": "TRK-774231-BD",
        "eta": "Delivered on March 8, 2026",
        "address": "Apt 4B, Gulshan 2, Dhaka",
        "payment": "Cash on Delivery",
    },
    "ORD-10061": {
        "items": [{"id": 43, "qty": 1}, {"id": 50, "qty": 3}],
        "total": 37.96,
        "status": "Processing",
        "tracking": "Awaiting dispatch",
        "eta": "March 15, 2026",
        "address": "Plot 7, Bashundhara R/A, Dhaka",
        "payment": "bKash",
    },
    "ORD-10078": {
        "items": [{"id": 13, "qty": 1}, {"id": 32, "qty": 1}],
        "total": 119.98,
        "status": "Out for Delivery",
        "tracking": "TRK-991102-BD",
        "eta": "Today by 9 PM",
        "address": "52 Mirpur Road, Dhaka",
        "payment": "Nagad",
    },
}

# ─────────────────────────────────────────────
# DISCOUNT CODES
# ─────────────────────────────────────────────
DISCOUNT_CODES = {
    "WELCOME10":  {"discount": 10, "type": "percent",  "desc": "10% off for new customers",          "min_order": 0},
    "SAVE20":     {"discount": 20, "type": "percent",  "desc": "20% off on orders above $100",       "min_order": 100},
    "FLAT15":     {"discount": 15, "type": "flat",     "desc": "$15 off your next order",            "min_order": 50},
    "TECH25":     {"discount": 25, "type": "percent",  "desc": "25% off Electronics category",       "min_order": 60},
    "FREESHIP":   {"discount": 0,  "type": "shipping", "desc": "Free shipping on any order",         "min_order": 0},
    "FLASH30":    {"discount": 30, "type": "percent",  "desc": "Flash sale — 30% off everything",   "min_order": 80},
}

# ─────────────────────────────────────────────
# FAQ & POLICIES
# ─────────────────────────────────────────────
FAQS = {
    "shipping": """🚚 *Shipping Policy*

• Standard delivery: 3–5 business days
• Express delivery: 1–2 business days (+$9.99)
• Free shipping on orders over $75
• Same-day delivery available in Dhaka (orders before 12 PM)
• International shipping: 7–14 business days""",

    "returns": """↩️ *Return & Refund Policy*

• 30-day hassle-free returns
• Items must be unused and in original packaging
• Refund processed within 3–5 business days after receiving return
• Electronics: 15-day return window
• No returns on personal care/beauty products (hygiene)
• Return shipping is FREE for defective items""",

    "payment": """💳 *Payment Methods*

We accept:
• Credit/Debit Cards (Visa, Mastercard)
• bKash, Nagad, Rocket
• Cash on Delivery (Dhaka only)
• PayPal
• Bank Transfer

All payments are 100% secure & encrypted 🔒""",

    "warranty": """🛡️ *Warranty Policy*

• Electronics: 1-year manufacturer warranty
• Smart devices: 2-year extended warranty available
• Defective items replaced within 7 days, no questions asked
• Warranty claims: send photo + order ID to support""",

    "cancellation": """❌ *Order Cancellation*

• Orders can be cancelled FREE within 1 hour of placing
• After 1 hour: $2 cancellation fee
• Once shipped: return process applies
• Refund for cancelled orders: 24–48 hours""",
}

# ─────────────────────────────────────────────
# SUPPORT ESCALATION
# ─────────────────────────────────────────────
SUPPORT_INFO = {
    "email":    "support@shopbot-demo.com",
    "phone":    "+880 1700-000000",
    "hours":    "Saturday–Thursday, 9 AM – 9 PM (BST)",
    "response": "We reply within 2 hours during business hours",
}
