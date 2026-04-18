"""
config.py — Style constants and theme tokens for the application.

Palette: #696B45 · #E0D5C9 · #C59D50 · #A37C40 · #392007 + neutral white
"""

# ── Primary Palette ──────────────────────────────────────────
DARK_BROWN   = "#392007"
OLIVE        = "#696B45"
GOLD         = "#C59D50"
AMBER        = "#A37C40"
BEIGE        = "#E0D5C9"
WHITE        = "#FAFAF8"

# ── Background colours ───────────────────────────────────────
BG           = BEIGE
SIDEBAR_BG   = DARK_BROWN
SIDEBAR_FG   = "#F5EDE3"       # Bright warm white — clearly visible
SIDEBAR_ACT  = OLIVE
SIDEBAR_HOVER = "#533115"      # Visible warm hover
TOPBAR_BG    = DARK_BROWN
CARD_BG      = WHITE

# ── Button colours ───────────────────────────────────────────
BTN_PRIMARY  = OLIVE
BTN_SUCCESS  = "#5B8C5A"
BTN_WARNING  = GOLD
BTN_DANGER   = "#C0392B"
BTN_SECONDARY = "#8C8C8C"
BTN_MUTED    = "#A89F95"

# ── Accent colours ───────────────────────────────────────────
ACCENT_GOLD  = GOLD
ACCENT_OLIVE = OLIVE
ACCENT_AMBER = AMBER

# ── Status / tag colours ────────────────────────────────────
STATUS_ACTIVE    = "#5B8C5A"
STATUS_LOW_STOCK = "#D4A017"
STATUS_EXPIRED   = "#C0392B"

# ── Row highlight colours (Treeview tags) ────────────────────
ROW_LOW_STOCK = "#FDF6E3"
ROW_EXPIRED   = "#FDE8E8"
ROW_SELECTED  = "#D5CEA3"
ROW_EVEN      = WHITE
ROW_ODD       = "#F0EBE4"

# ── Text colours ─────────────────────────────────────────────
TEXT_PRIMARY   = DARK_BROWN
TEXT_SECONDARY = "#6B5E50"
TEXT_MUTED     = "#9C8E7E"
TEXT_LIGHT     = "#D4C8BA"

# ── Input / border colours ───────────────────────────────────
INPUT_BORDER   = "#C4B9AD"
INPUT_FOCUS    = OLIVE
BORDER_LIGHT   = "#D6CEC4"

# ── Popover / dialog colours ─────────────────────────────────
POPOVER_BG      = WHITE
POPOVER_BORDER  = BORDER_LIGHT
POPOVER_OVERLAY = "#39200755"

# ── Typography ───────────────────────────────────────────────
FONT_FAMILY  = "Segoe UI"
ICON_FONT    = "Segoe MDL2 Assets"

FONT_SIZE_XL = 22
FONT_SIZE_LG = 16
FONT_SIZE_MD = 12
FONT_SIZE_SM = 10
FONT_SIZE_XS = 9

# ── Animation ────────────────────────────────────────────────
FADE_STEP     = 0.10
FADE_DELAY_MS = 12

# ── Spacing / sizing ────────────────────────────────────────
PAD_XS = 4
PAD_SM = 8
PAD_MD = 14
PAD_LG = 22
PAD_XL = 30
SIDEBAR_WIDTH = 220

# ── Chart colours ────────────────────────────────────────────
CHART_STOCK_IN  = OLIVE
CHART_STOCK_OUT = AMBER
CHART_GRID      = "#E5DDD3"
CHART_BG        = WHITE
