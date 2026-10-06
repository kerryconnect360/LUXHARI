from . import db
from .models import Product, Setting


def img(pid):
    return f'https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=1000'

# Real photography starter pool gathered from Pexels search results.
# The catalogue intentionally cycles a curated pool so the first deployment looks alive
# without storing hundreds of large image binaries in the repository.
CLOTHING_IMGS = [img(x) for x in [
    36594454, 39296295, 31772344, 13057803, 32054829, 8619007,
    11844471, 18794493, 15190577, 12727305, 16018021, 37945790,
    8676432, 34959076, 38098464, 33411617, 7779227, 13314583,
    833169, 19224974, 1075776, 31207622, 14760649, 914668,
    8445413, 31743090, 37851062, 34299200, 977909
]]
MATERIAL_IMGS = [img(x) for x in [
    236748, 7774245, 37271028, 9824794, 38928524, 34634858,
    5504775, 34005900, 36299785, 4452516, 36594454, 4721513,
    4452516
]]
HOME_IMGS = [img(x) for x in [
    33312398, 33326583, 5864643, 8210494, 8673107, 90317,
    10060915, 11701116, 262048
]]
ACCESSORY_IMGS = [img(x) for x in [
    29043373, 5301351, 7314460, 7314466, 28933801, 14587263,
    13155693, 28933799, 29013500, 12753202, 8705767, 28976815,
    28933800, 14579309, 13340660, 8886925, 12133990, 10526289,
    10164658, 13155692
]]

NAMES = {
    'Clothing': [
        'Satin Evening Dress', 'Ivory Column Dress', 'Tailored Wrap Dress', 'Midnight Slip Dress',
        'Soft Pleat Dress', 'Linen Day Dress', 'Structured Blazer', 'Relaxed Statement Jacket',
        'Wide-Leg Trousers', 'Silk Shirt', 'Cropped Tailoring Jacket', 'Fluid Maxi Dress',
        'Textured Midi Dress', 'Classic White Shirt', 'Velvet Evening Jacket', 'Minimal Jumpsuit',
        'Soft Knit Set', 'Pleated Skirt', 'Longline Coat', 'Sculpted Top'
    ],
    'Brands / Collections': [
        'The Atelier Edit', 'After Dark Collection', 'Quiet Luxury Edit', 'Modern Heritage',
        'Sunday Silk', 'Midnight Studio', 'Soft Structure', 'Golden Hour Edit', 'City Tailoring',
        'The Linen Chapter', 'Evening Forms', 'New Classics', 'The Signature Edit', 'Soft Power',
        'Resort Notes', 'The Monochrome Edit', 'Statement Neutrals', 'Modern Romance',
        'The Occasion Edit', 'Everyday Elegance'
    ],
    'Materials': [
        'Champagne Satin', 'Midnight Velvet', 'Ivory Linen', 'Emerald Jacquard', 'Rose Cotton',
        'Warm Taupe Suede', 'Cobalt Knit', 'Ruby Textile', 'Forest Quilted Fabric', 'Cream Brocade',
        'Plum Jersey', 'Sandstone Linen Blend', 'Graphite Wool', 'Pearl Organza', 'Golden Damask',
        'Ocean Blue Twill', 'Terracotta Cotton', 'Black Crepe', 'Soft Stone Canvas', 'Burgundy Velvet'
    ],
    'On Model': [
        'Look 01 — Midnight Tailoring', 'Look 02 — Soft Ivory', 'Look 03 — City Silk', 'Look 04 — Modern Black',
        'Look 05 — Rose Evening', 'Look 06 — Relaxed Linen', 'Look 07 — Statement Pink', 'Look 08 — Quiet Blue',
        'Look 09 — Garden Neutrals', 'Look 10 — After Dark', 'Look 11 — Classic White', 'Look 12 — Layered Texture',
        'Look 13 — Sharp Tailoring', 'Look 14 — Weekend Ease', 'Look 15 — Silver Night', 'Look 16 — Red Accent',
        'Look 17 — Soft Utility', 'Look 18 — Modern Romance', 'Look 19 — Black & Gold', 'Look 20 — Editorial White'
    ],
    'Home & Living': [
        'Cloud White Bedding Set', 'Midnight Velvet Curtains', 'Warm Ivory Sheer Curtains', 'Stonewashed Linen Throw',
        'Deep Blue Quilted Coverlet', 'Soft Sand Cushion Pair', 'Olive Texture Throw', 'Pearl White Duvet Set',
        'Warm Taupe Curtain Pair', 'Quiet Grey Bed Linen', 'Terracotta Cushion Pair', 'Sage Green Throw',
        'Cream Embroidered Pillow', 'Charcoal Velvet Cushion', 'Natural Linen Runner', 'Ivory Table Cloth',
        'Soft Gold Accent Cushion', 'Blue Window Drapes', 'Textured Bedspread', 'Weekend Guest Linen Set'
    ],
    'Accessories': [
        'Gold Link Bracelet', 'Pearl Drop Earrings', 'Classic Gold Bangle', 'Layered Chain Necklace',
        'Emerald Statement Ring', 'Silver Hoop Earrings', 'Fine Pendant Necklace', 'Beaded Bracelet Stack',
        'Sculpted Cuff', 'Crystal Drop Earrings', 'Gold Chain Belt', 'Vintage Watch Edit',
        'Statement Collar Necklace', 'Minimal Ring Set', 'Satin Evening Clutch', 'Soft Leather Handbag',
        'Silk Scarf — Champagne', 'Silk Scarf — Midnight', 'Slim Waist Belt', 'Polished Sunglasses'
    ],
    'Inspiration': [
        'How to Build a Tonal Look', 'The Art of Layering', 'A Quiet Evening Palette', 'Texture Meets Light',
        'Modern Tailoring in Motion', 'The New Neutral', 'Dressing for Golden Hour', 'Soft Drama',
        'City After Dark', 'Linen, Light & Space', 'Jewellery as a Finishing Detail', 'Black with Warm Metals',
        'The Shape of a Good Shirt', 'When Texture Leads', 'The Weekend Edit', 'Simple, Then Special',
        'The Modern Occasion', 'Details Worth Noticing', 'A Study in Ivory', 'Blue Hour Dressing'
    ],
}

PRODUCT_TYPES = {
    'Clothing': 'Clothing',
    'Brands / Collections': 'Collection',
    'Materials': 'Material',
    'On Model': 'On Model Look',
    'Home & Living': 'Home Textile',
    'Accessories': 'Accessory',
    'Inspiration': 'Editorial',
}

IMG_POOLS = {
    'Clothing': CLOTHING_IMGS,
    'Brands / Collections': CLOTHING_IMGS,
    'Materials': MATERIAL_IMGS,
    'On Model': CLOTHING_IMGS,
    'Home & Living': HOME_IMGS,
    'Accessories': ACCESSORY_IMGS,
    'Inspiration': CLOTHING_IMGS,
}

BASE_PRICES = {
    'Clothing': 6900,
    'Brands / Collections': 8500,
    'Materials': 1450,
    'On Model': 7900,
    'Home & Living': 6800,
    'Accessories': 2400,
    'Inspiration': 0,
}

DESCRIPTIONS = {
    'Clothing': 'Starter catalogue piece for the LUXHARI launch edit. Replace the photography, price and details through Authority before treating it as final stock.',
    'Brands / Collections': 'Starter collection story for the LUXHARI launch edit. Replace with your actual collection imagery and copy through Authority.',
    'Materials': 'Starter textile listing with real fabric photography. Update colour, composition, meterage, price and stock through Authority.',
    'On Model': 'Starter on-model look using real fashion photography. Link it to the exact LUXHARI garment by editing this listing in Authority.',
    'Home & Living': 'Starter home-textile listing using real interior photography. Replace with your own product photography and final specifications.',
    'Accessories': 'Starter accessory listing using real jewellery/accessory photography. Replace with your own item photography and exact product information.',
    'Inspiration': 'Starter editorial inspiration tile. Set price to 0 and use it as visual editorial content; replace or archive it through Authority.',
}


def _price(category, index):
    if category == 'Inspiration':
        return 0
    base = BASE_PRICES[category]
    if category == 'Materials':
        return base + (index % 7) * 225
    if category == 'Accessories':
        return base + (index % 9) * 350
    return base + (index % 11) * 600


def ensure_starter_catalog():
    """Ensure there are at least 50 starter records in every public category.

    Existing real/admin-created products are never altered. Missing starter entries are
    appended once per category, making the seed safe to run after a redeploy.
    """
    starter_counts = {
        c: Product.query.filter_by(category=c, archived=False).count()
        for c in NAMES
    }
    made = 0
    for category, names in NAMES.items():
        need = max(0, 50 - starter_counts.get(category, 0))
        pool = IMG_POOLS[category]
        for i in range(need):
            global_index = starter_counts.get(category, 0) + i
            name = names[global_index % len(names)]
            # Distinguish repeated starter slots while keeping names elegant.
            cycle = global_index // len(names) + 1
            if cycle > 1:
                name = f'{name} {cycle:02d}'
            is_editorial = category == 'Inspiration'
            product = Product(
                name=name,
                category=category,
                product_type=PRODUCT_TYPES[category],
                description=DESCRIPTIONS[category],
                price=_price(category, global_index),
                unit_label=('metre' if category == 'Materials' else 'item'),
                stock=(0 if is_editorial else 12 + (global_index % 18)),
                sizes=('S / M / L / XL' if category in {'Clothing', 'Brands / Collections', 'On Model'} else ''),
                external_image=pool[global_index % len(pool)],
                image=pool[global_index % len(pool)],
                featured=(global_index < 6),
                custom_order=False,
                archived=False,
                loves=0,
            )
            db.session.add(product)
            made += 1
    Setting.query.filter_by(key='starter_catalog_note').delete()
    db.session.add(Setting(
        key='starter_catalog_note',
        value=(
            'LUXHARI ships with a starter catalogue: at least 50 records in each public '
            'category using real Pexels photography. Prices/stock/names are launch placeholders. '
            'Replace or archive them from Authority as your actual inventory is entered.'
        ),
    ))
    return made
