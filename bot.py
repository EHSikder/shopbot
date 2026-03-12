"""
ShopBot — AI-Powered E-commerce Support Telegram Bot
=====================================================
Features:
  ✅ Browse products by category
  ✅ Search products by name
  ✅ Place orders (natural language)
  ✅ Track orders
  ✅ Returns & refunds
  ✅ Apply discount codes
  ✅ Wishlist management
  ✅ FAQ & policies
  ✅ Live support escalation
  ✅ AI-powered responses (Claude API)
  ✅ Persistent shopping cart
"""

import os
import re
import uuid
import json
import logging
import datetime
import anthropic
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from mock_data import (
    PRODUCTS, CATEGORIES, EXISTING_ORDERS,
    DISCOUNT_CODES, FAQS, SUPPORT_INFO
)

# ─────────────────────────────────────────────
# CONFIG — set these in your environment
# ─────────────────────────────────────────────
TELEGRAM_TOKEN  = os.environ.get("TELEGRAM_TOKEN", "YOUR_TELEGRAM_TOKEN_HERE")
ANTHROPIC_KEY   = os.environ.get("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_KEY_HERE")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# In-memory session store  { user_id: { cart, wishlist, orders, history } }
sessions = {}

def get_session(user_id: int) -> dict:
    if user_id not in sessions:
        sessions[user_id] = {
            "cart":     {},   # { product_id: qty }
            "wishlist": [],   # [ product_id, ... ]
            "orders":   {},   # { order_id: order_dict }
            "history":  [],   # [ { role, content }, ... ]  AI conversation
            "discount": None, # applied code
        }
    return sessions[user_id]


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def product_card(pid: int) -> str:
    p = PRODUCTS[pid]
    stars = "⭐" * round(p["rating"])
    stock_label = "✅ In Stock" if p["stock"] > 0 else "❌ Out of Stock"
    return (
        f"{p['emoji']} *#{pid} — {p['name']}*\n"
        f"💰 Price: *${p['price']:.2f}*\n"
        f"📦 Category: {p['category']}\n"
        f"{stars} {p['rating']}/5\n"
        f"{stock_label} ({p['stock']} left)"
    )

def cart_summary(session: dict) -> str:
    if not session["cart"]:
        return "🛒 Your cart is empty."
    lines = ["🛒 *Your Cart:*\n"]
    total = 0
    for pid, qty in session["cart"].items():
        p = PRODUCTS[pid]
        subtotal = p["price"] * qty
        total += subtotal
        lines.append(f"• {p['emoji']} #{pid} {p['name']} ×{qty} = ${subtotal:.2f}")
    discount = session.get("discount")
    if discount and discount in DISCOUNT_CODES:
        code = DISCOUNT_CODES[discount]
        if code["type"] == "percent":
            saving = total * code["discount"] / 100
            total -= saving
            lines.append(f"\n🏷️ Code `{discount}` applied: −{code['discount']}% (−${saving:.2f})")
        elif code["type"] == "flat":
            saving = min(code["discount"], total)
            total -= saving
            lines.append(f"\n🏷️ Code `{discount}` applied: −${saving:.2f}")
        elif code["type"] == "shipping":
            lines.append(f"\n🏷️ Code `{discount}` applied: Free Shipping!")
    lines.append(f"\n💵 *Total: ${total:.2f}*")
    return "\n".join(lines)

def generate_order_id() -> str:
    return f"ORD-{uuid.uuid4().hex[:5].upper()}"


# ─────────────────────────────────────────────
# MAIN MENU KEYBOARD
# ─────────────────────────────────────────────
def main_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["🛍️ Browse Products",  "🔍 Search Product"],
        ["🛒 My Cart",          "❤️ Wishlist"],
        ["📦 Track Order",      "↩️ Return / Refund"],
        ["🏷️ Discount Codes",   "❓ FAQ & Policies"],
        ["🤖 Ask AI Assistant", "📞 Contact Support"],
    ], resize_keyboard=True)


# ─────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_session(user.id)
    await update.message.reply_text(
        f"👋 Welcome to *ShopBot*, {user.first_name}!\n\n"
        "I'm your AI-powered shopping assistant 🛒\n"
        "I can help you:\n"
        "• 🛍️ Browse & search 60+ products\n"
        "• 📦 Place & track orders\n"
        "• ↩️ Handle returns & refunds\n"
        "• 🏷️ Apply discount codes\n"
        "• ❤️ Manage your wishlist\n"
        "• 🤖 Answer any question with AI\n\n"
        "Use the menu below or just *type naturally* — I understand you! 💬",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


# ─────────────────────────────────────────────
# BROWSE PRODUCTS
# ─────────────────────────────────────────────
async def browse_products(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(f"{emoji} {cat}", callback_data=f"cat_{cat}")]
        for cat, emoji in CATEGORIES.items()
    ]
    buttons.append([InlineKeyboardButton("🔥 All Products (Top Rated)", callback_data="cat_ALL")])
    await update.message.reply_text(
        "🛍️ *Browse by Category*\nChoose a category:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

async def show_category(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat = query.data.replace("cat_", "")

    if cat == "ALL":
        items = sorted(PRODUCTS.items(), key=lambda x: -x[1]["rating"])[:10]
        title = "🔥 Top Rated Products"
    else:
        items = [(pid, p) for pid, p in PRODUCTS.items() if p["category"] == cat]
        title = f"{CATEGORIES.get(cat, '')} {cat} Products"

    buttons = []
    for pid, p in items:
        label = f"{p['emoji']} #{pid} {p['name']} — ${p['price']:.2f}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"product_{pid}")])

    await query.edit_message_text(
        f"*{title}*\n\nTap any product to see details:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

async def show_product(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pid = int(query.data.replace("product_", ""))
    buttons = [
        [
            InlineKeyboardButton("🛒 Add to Cart",    callback_data=f"addcart_{pid}"),
            InlineKeyboardButton("❤️ Wishlist",       callback_data=f"addwish_{pid}"),
        ],
        [InlineKeyboardButton("⚡ Order Now",         callback_data=f"ordernow_{pid}")],
        [InlineKeyboardButton("◀️ Back",              callback_data="cat_ALL")],
    ]
    await query.edit_message_text(
        product_card(pid),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ─────────────────────────────────────────────
# SEARCH PRODUCTS
# ─────────────────────────────────────────────
async def search_prompt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["awaiting"] = "search"
    await update.message.reply_text(
        "🔍 *Product Search*\n\nType the product name or keyword (e.g. 'headphones', 'yoga', 'serum'):",
        parse_mode="Markdown",
    )

async def do_search(keyword: str, update: Update):
    kw = keyword.lower()
    results = [
        (pid, p) for pid, p in PRODUCTS.items()
        if kw in p["name"].lower() or kw in p["category"].lower()
    ]
    if not results:
        await update.message.reply_text(
            f"😕 No products found for *'{keyword}'*.\nTry a different keyword!",
            parse_mode="Markdown",
        )
        return
    buttons = [
        [InlineKeyboardButton(f"{p['emoji']} #{pid} {p['name']} — ${p['price']:.2f}", callback_data=f"product_{pid}")]
        for pid, p in results[:8]
    ]
    await update.message.reply_text(
        f"🔍 Found *{len(results)}* result(s) for '{keyword}':",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ─────────────────────────────────────────────
# CART
# ─────────────────────────────────────────────
async def add_to_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ Added to cart!")
    pid = int(query.data.replace("addcart_", ""))
    session = get_session(query.from_user.id)
    session["cart"][pid] = session["cart"].get(pid, 0) + 1
    await query.edit_message_text(
        product_card(pid) + f"\n\n✅ *Added to cart!* You have {session['cart'][pid]}×\n\nUse '🛒 My Cart' to view or checkout.",
        parse_mode="Markdown",
    )

async def show_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    session = get_session(update.effective_user.id)
    summary = cart_summary(session)
    buttons = []
    if session["cart"]:
        buttons = [
            [InlineKeyboardButton("✅ Checkout & Place Order", callback_data="checkout")],
            [InlineKeyboardButton("🗑️ Clear Cart",            callback_data="clearcart")],
        ]
    await update.message.reply_text(
        summary, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
    )

async def checkout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    session = get_session(query.from_user.id)
    if not session["cart"]:
        await query.edit_message_text("🛒 Your cart is empty!")
        return
    order_id = generate_order_id()
    total = sum(PRODUCTS[pid]["price"] * qty for pid, qty in session["cart"].items())
    discount = session.get("discount")
    if discount and discount in DISCOUNT_CODES:
        code = DISCOUNT_CODES[discount]
        if code["type"] == "percent":
            total *= (1 - code["discount"] / 100)
        elif code["type"] == "flat":
            total = max(0, total - code["discount"])
    session["orders"][order_id] = {
        "items":    dict(session["cart"]),
        "total":    round(total, 2),
        "status":   "Processing",
        "tracking": "Awaiting dispatch",
        "eta":      (datetime.date.today() + datetime.timedelta(days=4)).strftime("%B %d, %Y"),
    }
    session["cart"].clear()
    session["discount"] = None
    await query.edit_message_text(
        f"🎉 *Order Placed Successfully!*\n\n"
        f"📋 Order ID: `{order_id}`\n"
        f"💵 Total Charged: *${total:.2f}*\n"
        f"📦 Status: Processing\n"
        f"🚚 Expected Delivery: {session['orders'][order_id]['eta']}\n\n"
        f"You'll get a shipping update soon!\n"
        f"Track anytime using `{order_id}` 📦",
        parse_mode="Markdown",
    )

async def clear_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🗑️ Cart cleared!")
    get_session(query.from_user.id)["cart"].clear()
    await query.edit_message_text("🗑️ Cart cleared. Start fresh from *🛍️ Browse Products*!", parse_mode="Markdown")


# ─────────────────────────────────────────────
# ORDER NOW (single item fast checkout)
# ─────────────────────────────────────────────
async def order_now(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pid = int(query.data.replace("ordernow_", ""))
    p = PRODUCTS[pid]
    session = get_session(query.from_user.id)
    order_id = generate_order_id()
    eta = (datetime.date.today() + datetime.timedelta(days=4)).strftime("%B %d, %Y")
    session["orders"][order_id] = {
        "items":    {pid: 1},
        "total":    p["price"],
        "status":   "Processing",
        "tracking": "Awaiting dispatch",
        "eta":      eta,
    }
    await query.edit_message_text(
        f"⚡ *Instant Order Placed!*\n\n"
        f"{p['emoji']} *{p['name']}*\n"
        f"💰 ${p['price']:.2f}\n\n"
        f"📋 Order ID: `{order_id}`\n"
        f"📦 Status: Processing\n"
        f"🚚 ETA: {eta}\n\n"
        f"Use *📦 Track Order* → `{order_id}` to follow your package!",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────
# TRACK ORDER
# ─────────────────────────────────────────────
async def track_order_prompt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["awaiting"] = "track"
    await update.message.reply_text(
        "📦 *Track Your Order*\n\nEnter your Order ID (e.g. `ORD-10045`):",
        parse_mode="Markdown",
    )

async def do_track(order_id: str, update: Update, session: dict):
    order_id = order_id.upper().strip()
    order = session["orders"].get(order_id) or EXISTING_ORDERS.get(order_id)
    if not order:
        await update.message.reply_text(
            f"❌ Order `{order_id}` not found.\n\n"
            "💡 Demo tip: Try `ORD-10045`, `ORD-10032`, `ORD-10061`, or `ORD-10078`",
            parse_mode="Markdown",
        )
        return
    items_text = ""
    for pid, qty in order["items"].items():
        p = PRODUCTS.get(int(pid), {})
        items_text += f"  • {p.get('emoji','📦')} #{pid} {p.get('name','Item')} ×{qty}\n"
    status_emoji = {
        "Processing":       "⏳",
        "Shipped":          "🚚",
        "Out for Delivery": "🏃",
        "Delivered":        "✅",
    }.get(order["status"], "📦")
    await update.message.reply_text(
        f"📦 *Order Tracking — {order_id}*\n\n"
        f"🛒 Items:\n{items_text}\n"
        f"💵 Total: ${order['total']:.2f}\n"
        f"{status_emoji} Status: *{order['status']}*\n"
        f"🔎 Tracking No: `{order.get('tracking','N/A')}`\n"
        f"📅 ETA: {order['eta']}",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────
# RETURNS & REFUNDS
# ─────────────────────────────────────────────
async def return_refund(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["awaiting"] = "return"
    await update.message.reply_text(
        "↩️ *Return & Refund Request*\n\n"
        "Please send your Order ID and reason for return.\n"
        "Example: `ORD-10045 — Product arrived damaged`\n\n"
        "_You can also just describe the problem in plain text!_",
        parse_mode="Markdown",
    )

async def process_return(text: str, update: Update, session: dict):
    # extract order ID if present
    match = re.search(r"ORD-[A-Z0-9\-]+", text.upper())
    order_id = match.group() if match else None
    ref_id = f"REF-{uuid.uuid4().hex[:6].upper()}"
    msg = (
        f"↩️ *Return Request Submitted*\n\n"
        f"📋 Reference ID: `{ref_id}`\n"
    )
    if order_id:
        msg += f"🔗 Linked Order: `{order_id}`\n"
    msg += (
        f"📝 Reason logged: _{text[:80]}_\n\n"
        f"✅ Our team will review within *24 hours*.\n"
        f"💳 Refund (if approved) → 3–5 business days\n"
        f"📧 Confirmation sent to your email."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


# ─────────────────────────────────────────────
# WISHLIST
# ─────────────────────────────────────────────
async def add_to_wishlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("❤️ Added to wishlist!")
    pid = int(query.data.replace("addwish_", ""))
    session = get_session(query.from_user.id)
    if pid not in session["wishlist"]:
        session["wishlist"].append(pid)
    p = PRODUCTS[pid]
    await query.edit_message_text(
        product_card(pid) + "\n\n❤️ *Saved to your Wishlist!*",
        parse_mode="Markdown",
    )

async def show_wishlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    session = get_session(update.effective_user.id)
    if not session["wishlist"]:
        await update.message.reply_text(
            "❤️ Your wishlist is empty.\nBrowse products and tap *❤️ Wishlist* to save items!"
        )
        return
    buttons = [
        [InlineKeyboardButton(
            f"{PRODUCTS[pid]['emoji']} #{pid} {PRODUCTS[pid]['name']} — ${PRODUCTS[pid]['price']:.2f}",
            callback_data=f"product_{pid}"
        )]
        for pid in session["wishlist"]
    ]
    buttons.append([InlineKeyboardButton("🗑️ Clear Wishlist", callback_data="clearwish")])
    await update.message.reply_text(
        f"❤️ *Your Wishlist* ({len(session['wishlist'])} items):",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

async def clear_wishlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🗑️ Wishlist cleared!")
    get_session(query.from_user.id)["wishlist"].clear()
    await query.edit_message_text("🗑️ Wishlist cleared!", parse_mode="Markdown")


# ─────────────────────────────────────────────
# DISCOUNT CODES
# ─────────────────────────────────────────────
async def show_discounts(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["awaiting"] = "discount"
    lines = ["🏷️ *Active Discount Codes*\n"]
    for code, info in DISCOUNT_CODES.items():
        lines.append(f"• `{code}` — {info['desc']}")
        if info["min_order"] > 0:
            lines.append(f"  _(Min. order: ${info['min_order']})_")
    lines.append("\n💬 *Reply with a code to apply it to your cart!*")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def apply_discount(code: str, update: Update, session: dict):
    code = code.strip().upper()
    if code not in DISCOUNT_CODES:
        await update.message.reply_text(
            f"❌ Code `{code}` is not valid. Check available codes above!", parse_mode="Markdown"
        )
        return
    info = DISCOUNT_CODES[code]
    cart_total = sum(PRODUCTS[pid]["price"] * qty for pid, qty in session["cart"].items())
    if cart_total < info["min_order"]:
        await update.message.reply_text(
            f"⚠️ Code `{code}` requires a minimum order of *${info['min_order']:.2f}*.\n"
            f"Your cart total: *${cart_total:.2f}*",
            parse_mode="Markdown",
        )
        return
    session["discount"] = code
    await update.message.reply_text(
        f"✅ Code `{code}` applied!\n_{info['desc']}_\n\nGo to 🛒 *My Cart* to see updated total.",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────
# FAQ & POLICIES
# ─────────────────────────────────────────────
async def faq_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("🚚 Shipping",       callback_data="faq_shipping")],
        [InlineKeyboardButton("↩️ Returns",        callback_data="faq_returns")],
        [InlineKeyboardButton("💳 Payment",        callback_data="faq_payment")],
        [InlineKeyboardButton("🛡️ Warranty",       callback_data="faq_warranty")],
        [InlineKeyboardButton("❌ Cancellation",   callback_data="faq_cancellation")],
    ]
    await update.message.reply_text(
        "❓ *FAQ & Policies*\nChoose a topic:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

async def show_faq(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data.replace("faq_", "")
    await query.edit_message_text(FAQS.get(topic, "Not found."), parse_mode="Markdown")


# ─────────────────────────────────────────────
# CONTACT SUPPORT
# ─────────────────────────────────────────────
async def contact_support(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    s = SUPPORT_INFO
    await update.message.reply_text(
        f"📞 *Contact Support*\n\n"
        f"📧 Email: {s['email']}\n"
        f"📱 Phone: {s['phone']}\n"
        f"🕐 Hours: {s['hours']}\n"
        f"⚡ Response: {s['response']}\n\n"
        f"Or type your issue here and our AI will help right away! 🤖",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────
# AI ASSISTANT (Claude)
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are ShopBot, a friendly and efficient AI shopping assistant for an e-commerce store.

Store inventory: 60 products across Electronics, Fashion, Home & Kitchen, Sports, Books, Beauty.
You help customers: browse products, place orders, track orders, process returns, apply discounts, answer FAQs.

When a customer wants to ORDER: extract product ID and confirm back clearly.
When a customer asks about TRACKING: ask for their order ID.
When a customer asks about RETURNS: ask for order ID and reason.
When a customer asks about PRODUCTS: recommend relevant items by ID and name.
When a customer asks about DISCOUNTS: mention available codes: WELCOME10, SAVE20, FLAT15, TECH25, FREESHIP, FLASH30.

Be concise, friendly, use emojis naturally. Never make up prices or product IDs not in the catalog."""

async def ai_assistant(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["awaiting"] = "ai"
    await update.message.reply_text(
        "🤖 *AI Assistant Mode*\n\nAsk me anything! I can help with orders, products, tracking, refunds — all in natural language.\n\n_Type 'exit' to return to the main menu._",
        parse_mode="Markdown",
    )

async def call_claude(message: str, history: list) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    history.append({"role": "user", "content": message})
    # keep last 10 messages to avoid token overflow
    trimmed = history[-10:]
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=trimmed,
    )
    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    return reply


# ─────────────────────────────────────────────
# NATURAL LANGUAGE ORDER DETECTION
# ─────────────────────────────────────────────
def extract_order_intent(text: str):
    """Returns product_id if user wants to order a specific item."""
    text_lower = text.lower()
    order_keywords = ["order", "buy", "purchase", "i want", "i'd like", "get me", "can i get", "add to cart"]
    if not any(kw in text_lower for kw in order_keywords):
        return None
    match = re.search(r"#(\d+)", text)
    if match:
        pid = int(match.group(1))
        if pid in PRODUCTS:
            return pid
    # try product name matching
    for pid, p in PRODUCTS.items():
        if p["name"].lower()[:15] in text_lower:
            return pid
    return None

def extract_track_intent(text: str):
    match = re.search(r"ORD-[A-Z0-9\-]+", text.upper())
    return match.group() if match else None


# ─────────────────────────────────────────────
# MESSAGE ROUTER (handles all text messages)
# ─────────────────────────────────────────────
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    session = get_session(user_id)
    awaiting = ctx.user_data.get("awaiting")

    # ── Menu buttons ──
    if text == "🛍️ Browse Products":
        return await browse_products(update, ctx)
    if text == "🔍 Search Product":
        return await search_prompt(update, ctx)
    if text == "🛒 My Cart":
        return await show_cart(update, ctx)
    if text == "❤️ Wishlist":
        return await show_wishlist(update, ctx)
    if text == "📦 Track Order":
        return await track_order_prompt(update, ctx)
    if text == "↩️ Return / Refund":
        return await return_refund(update, ctx)
    if text == "🏷️ Discount Codes":
        return await show_discounts(update, ctx)
    if text == "❓ FAQ & Policies":
        return await faq_menu(update, ctx)
    if text == "🤖 Ask AI Assistant":
        return await ai_assistant(update, ctx)
    if text == "📞 Contact Support":
        return await contact_support(update, ctx)
    if text.lower() == "exit":
        ctx.user_data["awaiting"] = None
        await update.message.reply_text("🏠 Back to main menu!", reply_markup=main_menu_keyboard())
        return

    # ── Awaiting states ──
    if awaiting == "search":
        ctx.user_data["awaiting"] = None
        return await do_search(text, update)

    if awaiting == "track":
        ctx.user_data["awaiting"] = None
        return await do_track(text, update, session)

    if awaiting == "return":
        ctx.user_data["awaiting"] = None
        return await process_return(text, update, session)

    if awaiting == "discount":
        ctx.user_data["awaiting"] = None
        return await apply_discount(text, update, session)

    if awaiting == "ai":
        if not ANTHROPIC_KEY or ANTHROPIC_KEY == "YOUR_ANTHROPIC_KEY_HERE":
            await update.message.reply_text("⚙️ AI mode not configured. Please set ANTHROPIC_API_KEY.")
            return
        await update.message.reply_chat_action("typing")
        reply = await call_claude(text, session["history"])
        return await update.message.reply_text(reply, parse_mode="Markdown")

    # ── Natural language detection (even without AI mode) ──
    pid = extract_order_intent(text)
    if pid:
        p = PRODUCTS[pid]
        order_id = generate_order_id()
        eta = (datetime.date.today() + datetime.timedelta(days=4)).strftime("%B %d, %Y")
        session["orders"][order_id] = {
            "items":    {pid: 1},
            "total":    p["price"],
            "status":   "Processing",
            "tracking": "Awaiting dispatch",
            "eta":      eta,
        }
        await update.message.reply_text(
            f"✅ *Order Confirmed!*\n\n"
            f"{p['emoji']} *{p['name']}*\n"
            f"💰 ${p['price']:.2f}\n\n"
            f"📋 Order ID: `{order_id}`\n"
            f"📦 Status: Processing\n"
            f"🚚 Expected Delivery: {eta}\n\n"
            f"Thank you for shopping with ShopBot! 🎉",
            parse_mode="Markdown",
        )
        return

    order_id_in_text = extract_track_intent(text)
    if order_id_in_text:
        return await do_track(order_id_in_text, update, session)

    # ── Fallback: use Claude AI ──
    if ANTHROPIC_KEY and ANTHROPIC_KEY != "YOUR_ANTHROPIC_KEY_HERE":
        await update.message.reply_chat_action("typing")
        reply = await call_claude(text, session["history"])
        await update.message.reply_text(reply, parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "👋 I didn't quite get that! Use the menu buttons below or try:\n"
            "• _'Show me electronics'_\n"
            "• _'Order item #21'_\n"
            "• _'Track ORD-10045'_\n"
            "• _'Apply code SAVE20'_",
            parse_mode="Markdown",
        )


# ─────────────────────────────────────────────
# CALLBACK ROUTER
# ─────────────────────────────────────────────
async def callback_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if data.startswith("cat_"):       return await show_category(update, ctx)
    if data.startswith("product_"):   return await show_product(update, ctx)
    if data.startswith("addcart_"):   return await add_to_cart(update, ctx)
    if data.startswith("addwish_"):   return await add_to_wishlist(update, ctx)
    if data.startswith("ordernow_"):  return await order_now(update, ctx)
    if data.startswith("faq_"):       return await show_faq(update, ctx)
    if data == "checkout":            return await checkout(update, ctx)
    if data == "clearcart":           return await clear_cart(update, ctx)
    if data == "clearwish":           return await clear_wishlist(update, ctx)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 ShopBot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
