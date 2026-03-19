import asyncio
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.enums import ButtonStyle, ParseMode
from Melody import app

# ---------------------------------------------------------------------------
# Helper: build a translation table from two LISTS of chars (1-to-1 mapping)
# This avoids str.maketrans(str, str) which fails with multi-codepoint chars.
# ---------------------------------------------------------------------------
def _make_table(src: str, dst: list) -> dict:
    """Map each character in src to the corresponding element in dst."""
    return {ord(s): d for s, d in zip(src, dst)}

_LOWER = "abcdefghijklmnopqrstuvwxyz"
_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_DIGITS = "0123456789"

class Fonts:

    # ── Combining-character styles (applied dynamically) ─────────────────────
    _COMBINING = {
        "stinky":    "\u033e",
        "clouds":    "\u035c\u0361",
        "happy":     "\u0306\u0308",
        "sad":       "\u0311\u0308",
        "bubbles":   "\u0325\u0366",
        "underline": "\u035f",
        "rays":      "\u0489",
        "birds":     "\u0488",
        "slash":     "\u0338",
        "stop":      "\u20e0",
        "skyline":   "\u033a\u0346",
        "arrows":    "\u034e",
        "strike":    "\u0336",
        "frozen":    "\u0f19",
    }

    # ── Static translation tables ─────────────────────────────────────────────
    TABLES: dict = {}

    @classmethod
    def _build_tables(cls):
        alpha = _LOWER + _UPPER
        alphanum = alpha + _DIGITS

        # Each mapping list must match alphanum / alpha exactly.
        # Typewriter  (a-z A-Z)
        cls.TABLES["typewriter"] = _make_table(alpha, list(
            "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"
            "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"))

        # Outline (a-z A-Z 0-9)
        cls.TABLES["outline"] = _make_table(alphanum, list(
            "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"
            "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"
            "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"))

        # Bold Serif (a-z A-Z 0-9)
        cls.TABLES["serif"] = _make_table(alphanum, list(
            "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳"
            "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
            "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"))

        # Italic Serif Bold (a-z A-Z)
        cls.TABLES["bold_cool"] = _make_table(alpha, list(
            "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛"
            "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁"))

        # Italic Serif (a-z A-Z)
        cls.TABLES["cool"] = _make_table(alpha, list(
            "𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧"
            "𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍"))

        # Small Caps (a-z A-Z 0-9)
        cls.TABLES["smallcap"] = _make_table(alphanum, list(
            "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"))

        # Script (a-z A-Z)
        cls.TABLES["script"] = _make_table(alpha, list(
            "𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏"
            "𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"))

        # Bold Script (a-z A-Z)
        cls.TABLES["bold_script"] = _make_table(alpha, list(
            "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃"
            "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"))

        # Tiny superscript (a-z A-Z)
        cls.TABLES["tiny"] = _make_table(alpha, list(
            "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ"
            "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁᵛᵂˣʸᶻ"))

        # Comic (a-z A-Z)
        cls.TABLES["comic"] = _make_table(alpha, list(
            "ᗩᗷᑕᗪᗴᖴᘜᕼIᒍKᒪᗰᑎOᑭᑫᖇՏTᑌᐯᗯ᙭Yᘔ"
            "ᗩᗷᑕᗪᗴᖴᘜᕼIᒍKᒪᗰᑎOᑭᑫᖇՏTᑌᐯᗯ᙭Yᘔ"))

        # Bold Sans (a-z A-Z 0-9)
        cls.TABLES["sans"] = _make_table(alphanum, list(
            "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"
            "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
            "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"))

        # Bold Italic Sans (a-z A-Z)
        cls.TABLES["slant_sans"] = _make_table(alpha, list(
            "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯"
            "𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕"))

        # Italic Sans (a-z A-Z)
        cls.TABLES["slant"] = _make_table(alpha, list(
            "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"
            "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"))

        # Normal Sans (a-z A-Z)
        cls.TABLES["sim"] = _make_table(alpha, list(
            "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓"
            "𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹"))

        # Gothic (a-z A-Z)
        cls.TABLES["gothic"] = _make_table(alpha, list(
            "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷"
            "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"))

        # Bold Gothic (a-z A-Z)
        cls.TABLES["bold_gothic"] = _make_table(alpha, list(
            "𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟"
            "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅"))

        # Manga (a-z A-Z)
        cls.TABLES["magic"] = _make_table(alpha, list(
            "卂乃匚ᗪ乇千ᘜ卄|ﾌҜㄥ爪几ㄖ卩Ҩ尺丂ㄒㄩᐯ山乂ㄚ乙"
            "卂乃匚ᗪ乇千ᘜ卄|ﾌҜㄥ爪几ㄖ卩Ҩ尺丂ㄒㄩᐯ山乂ㄚ乙"))

        # Double-struck (a-z A-Z)
        cls.TABLES["double"] = _make_table(alpha, list(
            "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"
            "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"))

        # Ladybug (a-z A-Z)
        cls.TABLES["ladybug"] = _make_table(alpha, list(
            "ꍏꌃꏳꀷꏂꎇꁅꀍꀤ꒻ꀘ꒒ꎭꈤꂦᖘꆰꋪꌚ꓄ꀎ꒦ꅐꉧꌩꁴ"
            "ꍏꌃꏳꀷꏂꎇꁅꀍꀤ꒻ꀘ꒒ꎭꈤꂦᖘꆰꋪꌚ꓄ꀎ꒦ꅐꉧꌩꁴ"))

        # Rvnes / Ethiopian-like (a-z A-Z)
        cls.TABLES["rvnes"] = _make_table(alpha, list(
            "ልጌርዕቿቻኗዘጎጋጕረጠክዐየዒዪነፕሁሀሠሸሃጊ"
            "ልጌርዕቿቻኗዘጎጋጕረጠክዐየዒዪነፕሁሀሠሸሃጊ"))

        # Circles (a-z A-Z)
        cls.TABLES["circles"] = _make_table(alpha, list(
            "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"
            "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"))

        # Dark circles (a-z A-Z)
        cls.TABLES["dcircle"] = _make_table(alpha, list(
            "🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩"
            "🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩"))

        # Squares (a-z A-Z)
        cls.TABLES["squares"] = _make_table(alpha, list(
            "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"
            "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"))

        # Andalucia mix (a-z A-Z)
        cls.TABLES["andalucia"] = _make_table(alpha, list(
            "ꪖ᥇ᥴᦔꫀᠻᧁꫝ𝓲𝓳𝘬ꪶꪑꪀꪮρ𝘲𝘳𝘴𝓽ꪊꪜ᭙᥊ꪗɀ"
            "ꪖ᥇ᥴᦔꫀᠻᧁꫝ𝓲𝓳𝘬ꪶꪑꪀꪮρ𝘲𝘳𝘴𝓽ꪊꪜ᭙᥊ꪗɀ"))

# Build tables at class definition time
Fonts._build_tables()


# --- Applying styles ---
def apply_font(text: str, style: str) -> str:
    if style in Fonts._COMBINING:
        comb = Fonts._COMBINING[style]
        return "".join(c + comb if c.strip() else c for c in text)
    table = Fonts.TABLES.get(style)
    return text.translate(table) if table else text


# --- Background Task for Auto-Delete ---
async def auto_delete_task(message: Message, delay: int = 60):
    await asyncio.sleep(60)
    try:
        await message.delete()
    except Exception:
        pass


# --- UI Helpers ---
_BUTTONS_DATA = [
    ("𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛", "typewriter"), ("𝕆𝕦𝕥𝕝𝕚𝕟𝕖",     "outline"),    ("𝐒𝐞𝐫𝐢𝐟",       "serif"),
    ("𝑺𝒆𝒓𝒊𝒇",      "bold_cool"),  ("𝑆𝑒𝑟𝑖𝑓",        "cool"),       ("Sᴍᴀʟʟ Cᴀᴘs", "smallcap"),
    ("𝓈𝒸𝓇𝒾𝓅𝓉",     "script"),     ("𝓼𝓬𝓻𝓲𝓹𝓽",       "bold_script"),("ᵗⁱⁿʸ",        "tiny"),
    ("ᑕOᗰIᑕ",      "comic"),      ("𝗦𝗮𝗻𝘀",          "sans"),       ("𝙎𝙖𝙣𝙨",        "slant_sans"),
    ("𝘚𝘢𝘯𝘴",        "slant"),      ("𝖲𝖺𝗇𝗌",          "sim"),        ("𝔊𝔬𝔱𝔥𝔦𝔠",     "gothic"),
    ("𝕲𝖔𝖙𝖍𝖎𝖈",      "bold_gothic"),("Ⓒ Ⓘ Ⓡ Ⓒ Ⓛ Ⓔ", "circles"),    ("🅒🅘🅡🅒🅛🅔",    "dcircle"),
    ("🄵🄾🄽🅃",       "squares"),    ("ꍏꁅ꒒ꍏꍏ",        "ladybug"),    ("ልᎯᎽ",          "rvnes"),
    ("Ꭺ𝑛ᑕ𝑎𝑙",      "andalucia"),  ("爪卂ᘜ|匚",        "magic"),      ("𝕕𝕠𝕦𝕓𝕝𝕖",     "double"),
    ("a̾S̾t̾i̾k̾y̾",   "stinky"),     ("a͜͡C͜͡l͜͡o͜͡u͜͡d",    "clouds"),     ("ă̈H̆̈ă̈p̆̈p̆̈y̆̈",  "happy"),
    ("ȃ̈S̑ȃ̈d̑",      "sad"),        ("ḁͦB̥ͦu̥ͦb̥ͦs̥ͦ",    "bubbles"),    ("a͟U͟n͟d͟e͟r",    "underline"),
    ("a҉R҉a҉y҉s",   "rays"),       ("a҈B҈i҈r҈ds",    "birds"),      ("a̸S̸l̸a̸s̸h̸",   "slash"),
    ("a⃠S⃠t⃠o⃠p",   "stop"),       ("a̺͆S̺͆k̺͆y͆",     "skyline"),    ("a͎A͎r͎r͎o͎w",   "arrows"),
    ("a̶S̶t̶r̶i̶k̶e",  "strike"),     ("a༙F༙r༙o༙z̈en",    "frozen"),
]


def get_font_markup(user_id: int, page: int = 0) -> InlineKeyboardMarkup:
    # 6 fonts per page (2 rows of 3)
    limit = 6
    total_fonts = len(_BUTTONS_DATA)
    total_pages = (total_fonts + limit - 1) // limit
    
    # Ensure page is within bounds
    page = max(0, min(page, total_pages - 1))
    
    start = page * limit
    end = start + limit
    fonts_slice = _BUTTONS_DATA[start:end]
    
    keyboard = []
    row = []
    for label, style in fonts_slice:
        btn = InlineKeyboardButton(label, callback_data=f"f|{style}|{page}|{user_id}")
        btn.style = ButtonStyle.PRIMARY
        row.append(btn)
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Navigation row: [ < ] [ Page X/Y ] [ > ]
    nav_row = []
    
    # Left arrow
    prev_page = (page - 1) % total_pages
    nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"n|{prev_page}|{user_id}"))
    
    # Page indicator (not a button but shown as one)
    nav_row.append(InlineKeyboardButton(f"{page + 1} / {total_pages}", callback_data="none"))
    
    # Right arrow
    next_page = (page + 1) % total_pages
    nav_row.append(InlineKeyboardButton("➡️", callback_data=f"n|{next_page}|{user_id}"))
    
    keyboard.append(nav_row)

    # Close button
    close_btn = InlineKeyboardButton("🗑️ Cʟᴏsᴇ", callback_data=f"c|{user_id}")
    close_btn.style = ButtonStyle.DANGER
    keyboard.append([close_btn])
    
    return InlineKeyboardMarkup(keyboard)


# --- Command handler ---
@app.on_message(filters.command(["font", "fonts"]))
async def font_cmd_handler(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "» ᴜsᴀɢᴇ: <code>/font [text]</code> or reply to a message with <code>/font</code>",
            parse_mode=ParseMode.HTML
        )

    if len(message.command) >= 2:
        text = message.text.split(None, 1)[1]
    elif message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ""
    else:
        text = ""

    if not text.strip():
        return await message.reply_text("» ᴄᴏᴜʟᴅɴ'ᴛ ғɪɴᴅ ᴀɴʏ ᴛᴇxᴛ ᴛᴏ sᴛʏʟɪᴢᴇ.")

    sent_msg = await message.reply_text(
        text=(
            f"<b>» Font Converter</b>\n"
            f"────────────────────\n"
            f"🔡 <b>Original:</b> <code>{text}</code>\n"
            f"✨ <b>Preview:</b> <code>{text}</code>"
        ),
        reply_markup=get_font_markup(message.from_user.id, page=0),
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(auto_delete_task(sent_msg, 120))


# --- Callback handler ---
@app.on_callback_query(filters.regex(r"^(f|n|c)\|"))
async def font_callback_handler(client: Client, query: CallbackQuery):
    data = query.data.split("|")
    prefix = data[0]
    
    if prefix == "f":
        # Font selection: f|style|page|uid
        style, page, uid = data[1], int(data[2]), int(data[3])
    elif prefix == "n":
        # Navigation: n|page|uid
        page, uid = int(data[1]), int(data[2])
    elif prefix == "c":
        # Close: c|uid
        uid = int(data[1])
    else:
        return await query.answer()

    if query.from_user.id != uid:
        return await query.answer("» This menu is only for the command user!", show_alert=True)

    if prefix == "c":
        return await query.message.delete()

    if prefix == "n":
        # Just update the buttons
        return await query.message.edit_reply_markup(
            reply_markup=get_font_markup(uid, page=page)
        )

    # Font selection logic (prefix == "f")
    try:
        # Always read from the "🔡 Original:" line — never from styled preview
        raw_text = ""
        for line in query.message.text.split("\n"):
            if "🔡" in line and "Original:" in line:
                # Strip everything before the first colon after "Original"
                raw_text = line.split("Original:", 1)[1].strip()
                break
        if not raw_text:
            return await query.answer("» Original text not found. Try sending /font again.", show_alert=True)
    except Exception:
        return await query.answer("» Error extracting text.", show_alert=True)

    stylized = apply_font(raw_text, style)

    if stylized == raw_text:
        return await query.answer("» This style has no effect on ASCII-only text.")

    await query.message.edit_text(
        text=(
            f"<b>» Font Converter</b>\n"
            f"────────────────────\n"
            f"🔡 <b>Original:</b> <code>{raw_text}</code>\n"
            f"✨ <b>Preview:</b> <code>{stylized}</code>"
        ),
        reply_markup=get_font_markup(uid, page=page),
        parse_mode=ParseMode.HTML
    )
    await query.answer("» Style applied!")

__MODULE__ = "Fᴏɴᴛs"
__HELP__ = """
<b>Font Converter:</b>

• /font [text] — convert text to a stylish font (reply or inline text)
• Only the command user can interact with the menu
• Menu auto-deletes after 2 minutes
"""
