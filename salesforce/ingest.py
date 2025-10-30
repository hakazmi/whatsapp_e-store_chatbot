import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv
from urllib.parse import unquote, urlparse, parse_qs

# --- Load environment variables ---
load_dotenv()

# --- Connect to Salesforce ---
sf = Salesforce(
    username=os.getenv("SALESFORCE_USERNAME"),
    password=os.getenv("SALESFORCE_PASSWORD"),
    security_token=os.getenv("SALESFORCE_SECURITY_TOKEN"),
    domain=os.getenv("SALESFORCE_DOMAIN", "test")  # default to sandbox
)
print("✅ Connected to Salesforce for product ingestion")

# --- Helper: Clean Google redirect URLs ---
def clean_image_url(url: str) -> str:
    """Extract the real image link from a Google redirect URL."""
    if "google.com/imgres" in url:
        query = parse_qs(urlparse(url).query)
        if "imgurl" in query:
            return unquote(query["imgurl"][0])
    return url

# --- Get Standard Pricebook ---
pricebook_query = sf.query("SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1")
pricebook_id = pricebook_query["records"][0]["Id"]
print(f"📘 Standard Pricebook ID: {pricebook_id}")

# --- Demo product catalog ---
products = [
    # ===== Belts =====
    {
        "Name": "Men's Leather Belt - Classic Black",
        "ProductCode": "BELT001",
        "Family": "Accessories",
        "Color__c": "Black",
        "Size__c": "34-38 inches",
        "Description": "Crafted from high-quality genuine leather, this classic black belt features a polished silver buckle, adjustable fit for sizes 34-38 inches, durable stitching, and a timeless design suitable for both formal attire and casual outfits.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Leather%20Belt%20-%20Classic%20Black&imgurl=https%3A%2F%2Fazbelt.com%2Fcdn%2Fshop%2Fproducts%2FClassic-Black-Mens-Leather-Belt-Brass-Buckle-Front_711c0960-3d7b-476d-900a-46f66d89edd8_1200x.jpg%3Fv%3D1613240735&imgrefurl=https%3A%2F%2Fazbelt.com%2Fproducts%2Fclassic-narrow-black-1-25-leather-belt&docid=O6v7MULsqmcpEM&tbnid=tgb3E2_LBkwpkM&vet=12ahUKEwiko7KK7reQAxXpERAIHa8iI5IQM3oECBoQAA..i&w=1024&h=1024&hcb=2&ved=2ahUKEwiko7KK7reQAxXpERAIHa8iI5IQM3oECBoQAA",
        "Price__c": 49.99
    },
    {
        "Name": "Men's Leather Belt - Brown",
        "ProductCode": "BELT002",
        "Family": "Accessories",
        "Color__c": "Brown",
        "Size__c": "34-40 inches",
        "Description": "Made from 100% genuine leather, this stylish brown belt offers an adjustable length from 34-40 inches, a classic buckle, reinforced edges for longevity, and versatile styling for everyday wear.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Leather%20Belt%20-%20Brown&imgurl=https%3A%2F%2Fazbelt.com%2Fcdn%2Fshop%2Fproducts%2FDSC07205_cut_938x.jpg%3Fv%3D1613938576&imgrefurl=https%3A%2F%2Fazbelt.com%2Fproducts%2Fclassic-wide-1-75-espresso-leather-belt&docid=3aAcW1cTzu9ZBM&tbnid=9F-sYSaAKRtWpM&vet=12ahUKEwjNgoij7reQAxWxCRAIHedXM1sQM3oECB4QAA..i&w=938&h=938&hcb=2&ved=2ahUKEwjNgoij7reQAxWxCRAIHedXM1sQM3oECB4QAA",
        "Price__c": 44.99
    },
    {
        "Name": "Men's Reversible Belt - Black/Brown",
        "ProductCode": "BELT003",
        "Family": "Accessories",
        "Color__c": "Black/Brown",
        "Size__c": "32-42 inches",
        "Description": "Versatile reversible belt with black on one side and brown on the other, made from genuine leather, featuring a reversible silver buckle, adjustable from 32-42 inches, perfect for matching different outfits with durable construction and smooth finish.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Reversible%20Belt%20-%20Black%2FBrown&imgurl=https%3A%2F%2Fwww.ninesparis.com%2F37500-thickbox_default%2Freversible-belt-in-black-and-brown-james.jpg&imgrefurl=https%3A%2F%2Fwww.ninesparis.com%2F18651-reversible-belt-in-black-and-brown-james-3662414210160.html&docid=bMgeyP6DS37G_M&tbnid=T0xQ9peCLg6nNM&vet=12ahUKEwiH8Obo7reQAxVuHxAIHd2oFSAQM3oECB4QAA..i&w=800&h=800&hcb=2&ved=2ahUKEwiH8Obo7reQAxVuHxAIHd2oFSAQM3oECB4QAA",
        "Price__c": 54.99
    },
    {
"Name": "Men's Leather Belt - Tan",
"ProductCode": "BELT008",
"Family": "Accessories",
"Color__c": "Tan",
"Size__c": "34-40 inches",
"Description": "Premium tan leather belt with a classic buckle, adjustable fit for sizes 34-40 inches, durable stitching, and versatile design for casual or formal wear.",
"Image_URL__c": "http://ansonbelt.com/cdn/shop/products/35mm_Saddle_Tan_Leather_with_Traditional_in_Antiqued_Gold_84318a0f-8b08-467d-9ee6-192e76f8e3af.jpg?v=1551215881",
"Price__c": 49.99
},
{
"Name": "Men's Webbing Belt - Khaki",
"ProductCode": "BELT009",
"Family": "Accessories",
"Color__c": "Khaki",
"Size__c": "32-42 inches",
"Description": "Durable khaki webbing belt with a metal buckle, adjustable length from 32-42 inches, ideal for casual outfits and outdoor activities, lightweight and comfortable.",
"Image_URL__c": "https://m.media-amazon.com/images/I/614pXipbN-L._AC_UY1000_.jpg",
"Price__c": 29.99
},
{
"Name": "Men's Dress Belt - Silver Buckle Black",
"ProductCode": "BELT010",
"Family": "Accessories",
"Color__c": "Black",
"Size__c": "32-38 inches",
"Description": "Elegant black dress belt featuring a silver buckle, made from genuine leather, adjustable for sizes 32-38 inches, perfect for formal attire with a sleek finish.",
"Image_URL__c": "http://ansonbelt.com/cdn/shop/files/mens-black-leather-belt-strap-and-classic-buckle-in-silver-with-a-curve-1-25-inch-width.jpg?v=1684963965",
"Price__c": 59.99
},
{
"Name": "Men's Leather Belt - Navy",
"ProductCode": "BELT011",
"Family": "Accessories",
"Color__c": "Navy",
"Size__c": "32-40 inches",
"Description": "High-quality navy leather belt with adjustable fit for sizes 32-40 inches, classic buckle, durable and stylish for everyday use.",
"Image_URL__c": "http://ansonbelt.com/cdn/shop/files/mens-leather-belt-strap-in-navy-1.5-inch-width.jpg?v=1685479083",
"Price__c": 49.99
},
{
"Name": "Men's Buckle Belt - Silver",
"ProductCode": "BELT012",
"Family": "Accessories",
"Color__c": "Silver/Black",
"Size__c": "34-42 inches",
"Description": "Stylish silver buckle belt with black strap, adjustable from 34-42 inches, perfect for formal and casual outfits, made from premium materials.",
"Image_URL__c": "https://ansonbelt.com/cdn/shop/files/mens-classic-silver-buckle-front-view-1-25-inches-wide.jpg?v=1684347336&width=1946",
"Price__c": 54.99
},
{
"Name": "Men's Casual Belt - Brown Canvas",
"ProductCode": "BELT013",
"Family": "Accessories",
"Color__c": "Brown",
"Size__c": "30-38 inches",
"Description": "Casual brown canvas belt with braided design, adjustable fit, comfortable for daily wear, ideal for jeans and casual pants.",
"Image_URL__c": "https://eu-images.contentstack.com/v3/assets/blt7dcd2cfbc90d45de/blt5aca6a81296fe99e/60dbb2bfd9a5243b669ca892/4_145.jpg?format=pjpg&auto=webp&quality=75%2C90&width=3840",
"Price__c": 34.99
},

    # ===== Wallets =====
    {
        "Name": "Men's Bifold Wallet - Black Leather",
        "ProductCode": "WALLET001",
        "Family": "Accessories",
        "Color__c": "Black",
        "Size__c": "Standard",
        "Description": "This classic bifold wallet is made from premium black leather, featuring 6 card slots, a coin pocket, multiple bill compartments, RFID protection, and a slim profile for comfortable pocket carry.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Bifold%20Wallet%20-%20Black%20Leather&imgurl=http%3A%2F%2Fbountybustle.com%2Fcdn%2Fshop%2Ffiles%2F1_93528af2-cf06-4e58-a6c9-7ac4de719110.jpg%3Fv%3D1716036684&imgrefurl=https%3A%2F%2Fbountybustle.com%2Fproducts%2Fjj-black-leather-bifold-wallet-with-contrasting-stitch&docid=lPkYxfkOs5_HrM&tbnid=N0aP-u4UfQgqoM&vet=12ahUKEwjUguP_7reQAxVRNxAIHfQBAZ8QM3oECBcQAA..i&w=4000&h=4000&hcb=2&ved=2ahUKEwjUguP_7reQAxVRNxAIHfQBAZ8QM3oECBcQAA",
        "Price__c": 39.99
    },
    {
        "Name": "Men's Slim Wallet - Brown Leather",
        "ProductCode": "WALLET002",
        "Family": "Accessories",
        "Color__c": "Brown",
        "Size__c": "Slim",
        "Description": "Designed for minimalism, this slim brown leather wallet includes RFID blocking technology, several card slots, a cash compartment, and a compact size ideal for front pocket use.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Slim%20Wallet%20-%20Brown%20Leather&imgurl=https%3A%2F%2F5.imimg.com%2Fdata5%2FTR%2FUE%2FWS%2FSELLER-49620552%2Fmens-slim-leather-wallet.jpg&imgrefurl=https%3A%2F%2Fwww.indiamart.com%2Fproddetail%2Fmens-slim-leather-wallet-20643040291.html%3Fsrsltid%3DAfmBOorxZp0mCPBaaH75aPXPSBXILevPaY_hqXeCOHoP6XgnTCUb6GnH&docid=OzBVynilvkWpGM&tbnid=pGAmrjHl9HZGXM&vet=12ahUKEwi4u_uQ77eQAxVONRAIHbexAFMQM3oECB0QAA..i&w=500&h=500&hcb=2&ved=2ahUKEwi4u_uQ77eQAxVONRAIHbexAFMQM3oECB0QAA",
        "Price__c": 34.99
    },
    {
        "Name": "Men's Travel Wallet - Blue",
        "ProductCode": "WALLET003",
        "Family": "Accessories",
        "Color__c": "Navy Blue",
        "Size__c": "Large",
        "Description": "Perfect for travelers, this large navy blue wallet features a passport holder, multiple card slots, zippered coin pocket, bill sections, made from durable material with secure closures.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Travel%20Wallet%20-%20Blue&imgurl=https%3A%2F%2Fi5.walmartimages.com%2Fasr%2F3225adbd-8c70-4ef0-a3c5-d87f96f25ec2.0ff8dc557aad0b1ab78b6866a0d3b651.jpeg%3FodnHeight%3D768%26odnWidth%3D768%26odnBg%3DFFFFFF&imgrefurl=https%3A%2F%2Fwww.walmart.com%2Fip%2FCover-Protector-Travel-Wallet-for-Men-Women-Traveling-Blue%2F5109551583&docid=FEl4h-tMoA0mjM&tbnid=7W5z8fuBUV41QM&vet=12ahUKEwjIoqfI77eQAxXxU1UIHa3FNBYQM3oECBcQAA..i&w=768&h=768&hcb=2&itg=1&ved=2ahUKEwjIoqfI77eQAxXxU1UIHa3FNBYQM3oECBcQAA",
        "Price__c": 59.99
    },
    {
"Name": "Men's Bifold Wallet - Brown Leather",
"ProductCode": "WALLET009",
"Family": "Accessories",
"Color__c": "Brown",
"Size__c": "Standard",
"Description": "Classic brown leather bifold wallet with multiple card slots, bill compartment, RFID protection, and a durable design for everyday use.",
"Image_URL__c": "http://www.graphicimage.com/cdn/shop/files/WLM-HAR-BRN-2_fd9e006c-47ad-4c6e-bb73-716e757542b4.jpg?v=1684737127",
"Price__c": 39.99
},
{
"Name": "Men's Money Clip Wallet - Black",
"ProductCode": "WALLET010",
"Family": "Accessories",
"Color__c": "Black",
"Size__c": "Slim",
"Description": "Slim black wallet with integrated money clip, card slots, minimalist design, RFID blocking, ideal for front pocket carry.",
"Image_URL__c": "https://gentcreate.com/cdn/shop/files/The-interior-of-a-black-wallet-with-a-money-clip.jpg?v=1734724040&width=1000",
"Price__c": 29.99
},
{
"Name": "Men's Passport Wallet - Grey",
"ProductCode": "WALLET011",
"Family": "Accessories",
"Color__c": "Grey",
"Size__c": "Large",
"Description": "Spacious grey passport wallet with slots for passport, cards, and currency, made from durable material, perfect for travel with secure organization.",
"Image_URL__c": "https://kmmco.com/cdn/shop/files/greycypresspassportwallet.png?v=1747163855&width=1500",
"Price__c": 49.99
},
{
"Name": "Men's Trifold Wallet - Tan Leather",
"ProductCode": "WALLET012",
"Family": "Accessories",
"Color__c": "Tan",
"Size__c": "Standard",
"Description": "Spacious tan leather trifold wallet with multiple card slots, bill compartments, ID window, RFID protection, durable for everyday carry.",
"Image_URL__c": "https://buffalojackson.com/cdn/shop/files/denver_leather_trifold_wallet_autumn_brown_3_of_3_2000x.jpg?v=1750781571",
"Price__c": 44.99
},
{
"Name": "Men's Slim Card Holder - Black",
"ProductCode": "WALLET013",
"Family": "Accessories",
"Color__c": "Black",
"Size__c": "Slim",
"Description": "Minimalist black slim card holder with RFID blocking, holds multiple cards and cash, perfect for front pocket, sleek design.",
"Image_URL__c": "https://m.media-amazon.com/images/I/81h7QAujmWL._AC_UY1000_.jpg",
"Price__c": 24.99
},
{
"Name": "Men's Zipper Wallet - Brown",
"ProductCode": "WALLET014",
"Family": "Accessories",
"Color__c": "Brown",
"Size__c": "Standard",
"Description": "Secure brown zipper wallet with coin pocket, card slots, bill section, made from genuine leather, ideal for travel and daily use.",
"Image_URL__c": "https://m.media-amazon.com/images/I/61udAjMMThL._UY1000_.jpg",
"Price__c": 39.99
},

    # ===== Shoes =====
    {
        "Name": "Men's Formal Shoes - Oxford Black",
        "ProductCode": "SHOE001",
        "Family": "Footwear",
        "Color__c": "Black",
        "Size__c": "7-11",
        "Description": "Elegant black oxford shoes crafted from fine leather, with lace-up closure, cushioned insoles for all-day comfort, durable soles, available in sizes 7-11, ideal for formal occasions like weddings or business meetings.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Formal%20Shoes%20-%20Oxford%20Black&imgurl=http%3A%2F%2F1ststep.pk%2Fcdn%2Fshop%2Ffiles%2Feton_black_oxford_shoes_0111230_1.webp%3Fv%3D1728043615&imgrefurl=https%3A%2F%2F1ststep.pk%2Fproducts%2Feton-black-oxford-shoes-0111230%3Fsrsltid%3DAfmBOoqCOuLqswM63v4olWPE84eVbMHj_YhnGhZ2K_8F-zPnIYhw6o-7&docid=prkmzyva9bVfGM&tbnid=C8hb9Q8Monv8SM&vet=12ahUKEwjiwJnl77eQAxUHAhAIHWkcGCkQM3oECCYQAA..i&w=800&h=800&hcb=2&ved=2ahUKEwjiwJnl77eQAxUHAhAIHWkcGCkQM3oECCYQAA",
        "Price__c": 89.99
    },
    {
        "Name": "Men's Casual Sneakers - White",
        "ProductCode": "SHOE002",
        "Family": "Footwear",
        "Color__c": "White",
        "Size__c": "7-12",
        "Description": "Comfortable white casual sneakers featuring breathable mesh upper, cushioned soles for support, lace-up style, lightweight construction, available in sizes 7-12, perfect for daily wear and light activities.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Casual%20Sneakers%20-%20White&imgurl=https%3A%2F%2Fi5.walmartimages.com%2Fasr%2F5bf0642a-c1fc-4c0d-aed2-ee6f981fbc96.dd88f541cdc2db7b17937ff7770d285f.jpeg&imgrefurl=https%3A%2F%2Fwww.walmart.com%2Fip%2FMen-s-Fashion-Sneakers-White-Shoes-for-Men-Casual-Breathable-Shoes%2F10028220530&docid=jUfG1J7TR3aTNM&tbnid=npRngstJq8aYmM&vet=12ahUKEwjq5rX977eQAxVFExAIHSisFdIQM3oECCIQAA..i&w=954&h=1118&hcb=2&ved=2ahUKEwjq5rX977eQAxVFExAIHSisFdIQM3oECCIQAA",
        "Price__c": 69.99
    },
    {
        "Name": "Men's Loafers - Tan",
        "ProductCode": "SHOE003",
        "Family": "Footwear",
        "Color__c": "Tan",
        "Size__c": "8-11",
        "Description": "Stylish tan loafers made from soft leather, slip-on design for convenience, flexible rubber soles, cushioned footbed, sizes 8-11, suitable for semi-formal events or office casual looks.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Loafers%20-%20Tan&imgurl=https%3A%2F%2Fdiscountstore.pk%2Fcdn%2Fshop%2Ffiles%2F71QWjdbNz8L._AC_SY625.webp%3Fv%3D1738575102&imgrefurl=https%3A%2F%2Fdiscountstore.pk%2Fproducts%2Fcentrino-mens-loafers-tan-44-eu%3Fsrsltid%3DAfmBOoqvW5bh6oi4dLO6kx0fCBnetiZkmB4wTQMtsZPb60-7GjLV13Qk&docid=N8WT4HJNyD4fVM&tbnid=ApspCUHHS3QgIM&vet=12ahUKEwi53OGa8LeQAxUQR1UIHXXgA3oQM3oECBYQAA..i&w=600&h=600&hcb=2&itg=1&ved=2ahUKEwi53OGa8LeQAxUQR1UIHXXgA3oQM3oECBYQAA",
        "Price__c": 74.99
    },
    {
"Name": "Men's Chelsea Boots - Black Leather",
"ProductCode": "SHOE010",
"Family": "Footwear",
"Color__c": "Black",
"Size__c": "7-12",
"Description": "Sleek black leather Chelsea boots with elastic side panels, pull-on design, cushioned insoles, durable soles, sizes 7-12, versatile for casual or formal looks.",
"Image_URL__c": "https://thursdayboots.com/cdn/shop/products/1024x1024-Men-Duke-Black-2.jpg?v=1708643654&width=1024",
"Price__c": 99.99
},
{
"Name": "Men's Canvas Sneakers - Navy",
"ProductCode": "SHOE011",
"Family": "Footwear",
"Color__c": "Navy",
"Size__c": "7-12",
"Description": "Casual navy canvas sneakers with rubber soles, lace-up closure, breathable material, comfortable fit, sizes 7-12, great for everyday wear.",
"Image_URL__c": "https://nothingnew.com/cdn/shop/products/1024x1024-Men-LowTop-NavyWhite-LB2_1024x1024.jpg?v=1652120355",
"Price__c": 59.99
},
{
"Name": "Men's Derby Shoes - Brown Leather",
"ProductCode": "SHOE012",
"Family": "Footwear",
"Color__c": "Brown",
"Size__c": "7-11",
"Description": "Polished brown leather Derby shoes with lace-up design, comfortable lining, sturdy construction, sizes 7-11, suitable for business or formal occasions.",
"Image_URL__c": "http://www.rancourtandcompany.com/cdn/shop/products/Camden-Derby---Carolina-Brown-CXL_3c21e141-74eb-48cb-96ba-efa47bea9979.jpg?v=1652996058",
"Price__c": 84.99
},
{
"Name": "Men's Hiking Boots - Grey",
"ProductCode": "SHOE013",
"Family": "Footwear",
"Color__c": "Grey",
"Size__c": "8-12",
"Description": "Rugged grey hiking boots with waterproof membrane, supportive cushioning, traction soles, lace-up fit, sizes 8-12, designed for trails and outdoor adventures.",
"Image_URL__c": "https://foxelli.com/cdn/shop/products/1R4A5008_2000x.jpg?v=1640085968",
"Price__c": 109.99
},
{
"Name": "Men's Flip Flops - Black",
"ProductCode": "SHOE014",
"Family": "Footwear",
"Color__c": "Black",
"Size__c": "8-12",
"Description": "Comfortable black flip flops with contoured footbed, durable straps, non-slip soles, sizes 8-12, perfect for beach or casual summer wear.",
"Image_URL__c": "https://olukai.com/cdn/shop/files/10110_4040_105_M_Ohana_BlackBlack_png.jpg?width=750",
"Price__c": 24.99
},
{
"Name": "Men's Monk Strap Shoes - Black",
"ProductCode": "SHOE015",
"Family": "Footwear",
"Color__c": "Black",
"Size__c": "7-11",
"Description": "Elegant black monk strap shoes with double buckle, leather upper, comfortable insoles, sizes 7-11, suitable for formal occasions.",
"Image_URL__c": "https://thursdayboots.com/cdn/shop/products/1024x1024-Men-Saint3.0-Black-122322-3.4_1024x1024.jpg?v=1674674244",
"Price__c": 89.99
},
{
"Name": "Men's Trail Running Shoes - Green",
"ProductCode": "SHOE016",
"Family": "Footwear",
"Color__c": "Green",
"Size__c": "8-12",
"Description": "Durable green trail running shoes with grip soles, breathable mesh, cushioning for comfort, sizes 8-12, designed for off-road running.",
"Image_URL__c": "https://lennyshoe.com/cdn/shop/files/new-balance-mens-more-trail-v2-running-shoes-green-524595.jpg?v=1721471002",
"Price__c": 79.99
},
{
"Name": "Men's Espadrilles - Beige",
"ProductCode": "SHOE017",
"Family": "Footwear",
"Color__c": "Beige",
"Size__c": "7-12",
"Description": "Casual beige espadrilles with jute soles, slip-on style, lightweight and breathable, sizes 7-12, perfect for summer outings.",
"Image_URL__c": "https://www.muloshoes.com/wp-content/uploads/Mens-Summer-Espadrilles-in-Sustainable-Linen-scaled.jpg",
"Price__c": 59.99
},
{
"Name": "Men's Work Boots - Brown",
"ProductCode": "SHOE018",
"Family": "Footwear",
"Color__c": "Brown",
"Size__c": "8-13",
"Description": "Rugged brown work boots with steel toe, waterproof leather, supportive cushioning, sizes 8-13, ideal for construction or heavy-duty work.",
"Image_URL__c": "http://www.overlookboots.com/cdn/shop/products/danner-mens-bull-run-usa-made-6-moc-steel-toe-work-boot-brown-15564.jpg?v=1751402356",
"Price__c": 109.99
},
{
"Name": "Men's Formal Loafers - Burgundy",
"ProductCode": "SHOE019",
"Family": "Footwear",
"Color__c": "Burgundy",
"Size__c": "7-11",
"Description": "Sophisticated burgundy formal loafers with penny strap, polished leather, slip-on design, sizes 7-11, great for business attire.",
"Image_URL__c": "https://n.nordstrommedia.com/it/ae5a3112-c63d-430f-90f7-fe78e6e316b8.jpeg?h=368&w=240&dpr=2",
"Price__c": 74.99
},

    # ===== Watches =====
    {
        "Name": "Men's Chronograph Watch - Silver Steel",
        "ProductCode": "WATCH001",
        "Family": "Watches",
        "Color__c": "Silver",
        "Size__c": "42mm",
        "Description": "Classic silver chronograph watch with stainless steel strap, water-resistant up to 50 meters, precise quartz movement, sub-dials for stopwatch functions, tachymeter bezel, 42mm case size for a bold look.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Chronograph%20Watch%20-%20Silver%20Steel&imgurl=https%3A%2F%2Ffossil.scene7.com%2Fis%2Fimage%2FFossilPartners%2FFS5384_main%3F%24sfcc_fos_medium%24&imgrefurl=https%3A%2F%2Fwww.fossil.com%2Fen-us%2Fwatches%2Fmens-watches%2Fstainless-steel-watches%2F&docid=BokjW5uKv6MA-M&tbnid=-2QpbVZtN0uyLM&vet=12ahUKEwimh5y48LeQAxWHBxAIHdwdF3gQM3oECCwQAA..i&w=300&h=348&hcb=2&ved=2ahUKEwimh5y48LeQAxWHBxAIHdwdF3gQM3oECCwQAA",
        "Price__c": 129.99
    },
    {
        "Name": "Men's Analog Watch - Leather Strap Brown",
        "ProductCode": "WATCH002",
        "Family": "Watches",
        "Color__c": "Brown",
        "Size__c": "40mm",
        "Description": "Elegant analog watch featuring a genuine brown leather strap, crisp white dial with date window, water-resistant casing, reliable movement, 40mm diameter, versatile for casual or professional settings.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Analog%20Watch%20-%20Leather%20Strap%20Brown&imgurl=https%3A%2F%2Foneclickshopping.pk%2Fwp-content%2Fuploads%2F2022%2F04%2FUntitled-1-96.jpg&imgrefurl=https%3A%2F%2Foneclickshopping.pk%2Fproduct%2Fwatch-for-men-analog-watch-business-watch-brown-leather-straps-stylish-wrist%2F&docid=DEQjWjSPu6qhOM&tbnid=OcN19xf9bZ03VM&vet=12ahUKEwi11YTR8LeQAxXETlUIHS8aAZ4QM3oECB4QAA..i&w=420&h=420&hcb=2&ved=2ahUKEwi11YTR8LeQAxXETlUIHS8aAZ4QM3oECB4QAA",
        "Price__c": 99.99
    },
    {
        "Name": "Men's Digital Sports Watch - Black",
        "ProductCode": "WATCH003",
        "Family": "Watches",
        "Color__c": "Black",
        "Size__c": "45mm",
        "Description": "Black digital sports watch with water resistance up to 100 meters, stopwatch, alarm, LED backlight for low-light visibility, durable resin strap, 45mm case, ideal for active lifestyles.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Digital%20Sports%20Watch%20-%20Black&imgurl=https%3A%2F%2Fm.media-amazon.com%2Fimages%2FI%2F71E9svLCYVL._AC_SL1500_.jpg&imgrefurl=https%3A%2F%2Fwww.ubuy.com.pk%2Fen%2Fproduct%2F1192BDLG-beeasy-mens-digital-sports-watch-waterproof-with-stopwatch-countdown-timer-alarm-mode-dual-time-watc%3Fsrsltid%3DAfmBOop918arac5bme1e-fpF0t9K9Au2CPP3-yw38kiUbfjpwJ-GJ4U0&docid=OA2G-IPiYf9d6M&tbnid=SNBfmR_5pJutKM&vet=12ahUKEwiL3tfp8LeQAxVpIhAIHbT6JvcQM3oECBYQAA..i&w=1081&h=1500&hcb=2&ved=2ahUKEwiL3tfp8LeQAxVpIhAIHbT6JvcQM3oECBYQAA",
        "Price__c": 79.99
    },
    {
"Name": "Men's Pilot Watch - Black",
"ProductCode": "WATCH011",
"Family": "Watches",
"Color__c": "Black",
"Size__c": "44mm",
"Description": "Black pilot watch with luminous hands, chronograph functions, stainless steel case, water-resistant, 44mm diameter, ideal for aviation enthusiasts.",
"Image_URL__c": "https://www.mvmt.com/dw/image/v2/BDKZ_PRD/on/demandware.static/-/Sites-mgi-master/default/dw679bef22/images/products/28000232_fr.jpg?sw=1660&sh=1660",
"Price__c": 139.99
},
{
"Name": "Men's Dress Watch - Gold",
"ProductCode": "WATCH012",
"Family": "Watches",
"Color__c": "Gold",
"Size__c": "40mm",
"Description": "Elegant gold dress watch with leather strap, minimalist dial, precise movement, water-resistant, 40mm case, perfect for formal occasions.",
"Image_URL__c": "https://cdn.shopify.com/s/files/1/0278/9723/3501/files/Hamilton-Intra-Matic-YG-2.jpg?v=1662495825",
"Price__c": 119.99
},
{
"Name": "Men's Solar Watch - Silver",
"ProductCode": "WATCH013",
"Family": "Watches",
"Color__c": "Silver",
"Size__c": "42mm",
"Description": "Silver solar-powered watch with eco-friendly charging, date display, stainless steel band, water-resistant, 42mm case, reliable for daily use.",
"Image_URL__c": "https://www.perryellis.com/cdn/shop/files/Perry-Ellis-mens-Solar-Powered-Silver-Stainless-Steel-Watch-Watches-Silver-gray_2e9720aa.jpg?v=1759349552&width=1080",
"Price__c": 99.99
},
{
"Name": "Men's Skeleton Watch - Rose Gold",
"ProductCode": "WATCH014",
"Family": "Watches",
"Color__c": "Rose Gold",
"Size__c": "43mm",
"Description": "Rose gold skeleton watch revealing intricate mechanics, automatic movement, sapphire crystal, water-resistant, 43mm case, a luxurious timepiece.",
"Image_URL__c": "https://aura.watch/cdn/shop/files/Rose-Link-Skeleton1-Flat-40mm.jpg?v=1740066085&width=1866",
"Price__c": 159.99
},
{
"Name": "Men's Field Watch - Green",
"ProductCode": "WATCH015",
"Family": "Watches",
"Color__c": "Green",
"Size__c": "42mm",
"Description": "Rugged green field watch with nylon strap, luminous markers, water-resistant, 42mm case, suitable for outdoor adventures.",
"Image_URL__c": "https://wolbrook.com/cdn/shop/products/Outrider-Professional-Mecaquartz-38mm-Field-Watch-French-Army-Green-Dial-Green-Nylon-Strap-22-OPM-003-NYL-GRN-LAF_565x720_crop_center.jpg?v=1705495605",
"Price__c": 129.99
},
{
"Name": "Men's Quartz Watch - Black",
"ProductCode": "WATCH016",
"Family": "Watches",
"Color__c": "Black",
"Size__c": "40mm",
"Description": "Sleek black quartz watch with leather strap, chronograph functions, date display, 40mm diameter, versatile for casual wear.",
"Image_URL__c": "https://i5.walmartimages.com/asr/c1ddc860-8a46-4502-8ba4-fc42d4bef952.69d3b5b939b42026148b4c6bc2b38637.jpeg?odnHeight=768&odnWidth=768&odnBg=FFFFFF",
"Price__c": 99.99
},
{
"Name": "Men's Smart Fitness Watch - Grey",
"ProductCode": "WATCH017",
"Family": "Watches",
"Color__c": "Grey",
"Size__c": "44mm",
"Description": "Grey smart fitness watch with heart rate monitor, activity tracking, Bluetooth calls, waterproof, 44mm screen, compatible with smartphones.",
"Image_URL__c": "https://i5.walmartimages.com/seo/Smart-Watches-Men-Answer-Make-Calls-1-91-HD-Fitness-Outdoor-Sports-Rugged-Smart-Watch-Android-iPhone-Waterproof-Fitness-Tracker-100-Sport-Modes-Watch_0ccf6258-dbe8-4809-a2ec-3f3e66ebe682.974e8b702bf71a6d7d24efe7437302b0.jpeg?odnHeight=768&odnWidth=768&odnBg=FFFFFF",
"Price__c": 149.99
},
{
"Name": "Men's Vintage Watch - Brown Leather",
"ProductCode": "WATCH018",
"Family": "Watches",
"Color__c": "Brown",
"Size__c": "38mm",
"Description": "Vintage-style watch with brown leather strap, rectangular dial, Roman numerals, quartz movement, 38mm case, elegant for classic looks.",
"Image_URL__c": "https://www.peugeotwatches.com/cdn/shop/products/2051GBR-FV_dff62fba-3c09-40ca-a12f-4322a9e71746.jpg?v=1633106959&width=1500",
"Price__c": 109.99
},

    # ===== NEW: Trousers =====
    {
        "Name": "Men's Dress Pants - Navy Blue",
        "ProductCode": "TROUSER001",
        "Family": "Clothing",
        "Color__c": "Navy Blue",
        "Size__c": "30-40",
        "Description": "Classic navy blue dress pants made from stretch cotton blend, flat front design, perfect for office wear or formal occasions, available in waist sizes 30-40 with multiple length options.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Dress%20Pants%20-%20Navy%20Blue&imgurl=https%3A%2F%2Fsfycdn.speedsize.com%2F2780c694-3419-4266-9652-d242439affeb%2Fstateandliberty.com%2Fcdn%2Fshop%2Ffiles%2F1HeatheredNavySuit3_cc590791-8421-494c-9c87-50b2c0c17208.jpg%3Fv%3D1747764499%26width%3D892&imgrefurl=https%3A%2F%2Fstateandliberty.com%2Fproducts%2Fathletic-fit-stretch-suit-pants-heathered-navy%3Fsrsltid%3DAfmBOorsKLeyStq8NxJYloEBma5KjAmaorNxXtlMIyLD18JH-OO8o4ke&docid=fE3cia5GnxWQlM&tbnid=LSXmNYBbfRM3WM&vet=12ahUKEwj297jV8reQAxVvTVUIHQi6AGcQM3oECBsQAA..i&w=892&h=1114&hcb=2&ved=2ahUKEwj297jV8reQAxVvTVUIHQi6AGcQM3oECBsQAA",
        "Price__c": 59.99
    },
    {
        "Name": "Men's Chino Pants - Khaki",
        "ProductCode": "TROUSER002",
        "Family": "Clothing",
        "Color__c": "Khaki",
        "Size__c": "30-42",
        "Description": "Versatile khaki chino pants with comfortable cotton fabric, straight leg fit, multiple pockets, and durable construction. Perfect for casual Friday or weekend outings.",
        "Image_URL__c": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=500&h=500&fit=crop",
        "Price__c": 49.99
    },
    {
        "Name": "Men's Slim Fit Trousers - Black",
        "ProductCode": "TROUSER003",
        "Family": "Clothing",
        "Color__c": "Black",
        "Size__c": "28-38",
        "Description": "Modern slim fit black trousers with stretch fabric for comfort, tapered leg design, perfect for both business casual and evening wear. Available in slim waist sizes 28-38.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Slim%20Fit%20Trousers%20-%20Black&imgurl=https%3A%2F%2Fxcdn.next.co.uk%2Fcommon%2Fitems%2Fdefault%2Fdefault%2Fitemimages%2F3_4Ratio%2Fproduct%2Flge%2F332484s.jpg%3Fim%3DResize%2Cwidth%3D750&imgrefurl=https%3A%2F%2Fwww.nextdirect.com%2Fpk%2Fen%2Fstyle%2Fst298599%2F332484&docid=v6bxfqBLgK5vPM&tbnid=ApdduGpankqqPM&vet=12ahUKEwjarsvv8reQAxUiU1UIHR2dKTkQM3oECBYQAA..i&w=750&h=1000&hcb=2&ved=2ahUKEwjarsvv8reQAxUiU1UIHR2dKTkQM3oECBYQAA",
        "Price__c": 54.99
    },
    {
        "Name": "Men's Cargo Pants - Olive Green",
        "ProductCode": "TROUSER004",
        "Family": "Clothing",
        "Color__c": "Olive Green",
        "Size__c": "32-44",
        "Description": "Durable olive green cargo pants with multiple utility pockets, reinforced stitching, comfortable fit for outdoor activities or casual wear. Made from tough cotton twill fabric.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Cargo%20Pants%20-%20Olive%20Green&imgurl=https%3A%2F%2Fpantproject.com%2Fcdn%2Fshop%2Ffiles%2Fcargo-joggers.jpg%3Fv%3D1736360767&imgrefurl=https%3A%2F%2Fpantproject.com%2Fproducts%2Fgreen-ripstop-textured-cargo-pants%3Fsrsltid%3DAfmBOorcnS0gx8kSQVDLksFcifi21S7EwbJYSQH-E3-wfzUK2MeK5YNL&docid=h-ave0YuSQomuM&tbnid=dnQFD0ZYNHQAVM&vet=12ahUKEwjwoZWH87eQAxU2HRAIHacUKhsQM3oECB4QAA..i&w=720&h=1080&hcb=2&ved=2ahUKEwjwoZWH87eQAxU2HRAIHacUKhsQM3oECB4QAA",
        "Price__c": 44.99
    },
    {
        "Name": "Men's Linen Trousers - Beige",
        "ProductCode": "TROUSER005",
        "Family": "Clothing",
        "Color__c": "Beige",
        "Size__c": "30-40",
        "Description": "Lightweight beige linen trousers perfect for summer, breathable fabric, relaxed fit, and elegant appearance. Ideal for warm weather occasions and vacation wear.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Linen%20Trousers%20-%20Beige&imgurl=http%3A%2F%2Fsir.se%2Fcdn%2Fshop%2Fproducts%2FDSC09657-WEB.jpg%3Fv%3D1652439383&imgrefurl=https%3A%2F%2Fsir.se%2Fproducts%2Fwalden-beige-linen-trousers%3Fsrsltid%3DAfmBOoprEt2nhPa9lH1EfC8Zi34afO0N0RmtxBmzG0YbbYkSRbpl_muI&docid=HR5CH7UtKrbBmM&tbnid=c5IBBJS-dNST_M&vet=12ahUKEwif-Zef87eQAxXIUFUIHeS0AOsQM3oECCUQAA..i&w=1200&h=1500&hcb=2&ved=2ahUKEwif-Zef87eQAxXIUFUIHeS0AOsQM3oECCUQAA",
        "Price__c": 39.99
    },
    {
"Name": "Men's Jeans - Blue Denim",
"ProductCode": "PANTS002",
"Family": "Apparel",
"Color__c": "Blue",
"Size__c": "30-38",
"Description": "Classic blue denim jeans with slim fit, durable cotton material, five-pocket design, sizes 30-38 waist, ideal for everyday casual outfits.",
"Image_URL__c": "https://shopduer.com/cdn/shop/files/MFLS3002-Perfromance_Denim_Silm_Heritage_Rinse_0081_R-967121.jpg?v=1744050035&width=1143",
"Price__c": 69.99
},
{
"Name": "Men's Dress Pants - Black",
"ProductCode": "PANTS003",
"Family": "Apparel",
"Color__c": "Black",
"Size__c": "32-40",
"Description": "Formal black dress pants with tailored fit, wool blend fabric, crease-resistant, sizes 32-40 waist, perfect for business or formal events.",
"Image_URL__c": "https://www.gentlemansguru.com/wp-content/uploads/2018/05/Mens-Formal-Black-Dress-Pants-from-Gentlemansguru.com_-scaled.jpg",
"Price__c": 79.99
},
{
"Name": "Men's Cargo Pants - Olive",
"ProductCode": "PANTS004",
"Family": "Apparel",
"Color__c": "Olive",
"Size__c": "30-38",
"Description": "Practical olive cargo pants with multiple pockets, relaxed fit, durable fabric, sizes 30-38 waist, great for outdoor activities.",
"Image_URL__c": "https://m.media-amazon.com/images/I/71F9KJ353EL._AC_UY1000_.jpg",
"Price__c": 59.99
},
{
"Name": "Men's Slim Fit Trousers - Grey",
"ProductCode": "PANTS005",
"Family": "Apparel",
"Color__c": "Grey",
"Size__c": "32-40",
"Description": "Slim fit grey trousers with tailored design, comfortable stretch fabric, sizes 32-40 waist, ideal for business casual.",
"Image_URL__c": "https://m.media-amazon.com/images/I/61EH9au1qUL._AC_UY1000_.jpg",
"Price__c": 69.99
},
{
"Name": "Men's Joggers - Black",
"ProductCode": "PANTS006",
"Family": "Apparel",
"Color__c": "Black",
"Size__c": "S-XXL",
"Description": "Comfortable black joggers with drawstring waist, tapered legs, soft material, sizes S-XXL, perfect for lounging or workouts.",
"Image_URL__c": "https://freshcleantees.com/cdn/shop/files/aa6bc3be90dce1c28b6b5d4c41a27dcd92201d6b-1500x2000.png?v=1707432116",
"Price__c": 49.99
},

    # ===== NEW: Shirts =====
    {
        "Name": "Men's Dress Shirt - White",
        "ProductCode": "SHIRT001",
        "Family": "Clothing",
        "Color__c": "White",
        "Size__c": "S-XXL",
        "Description": "Classic white dress shirt made from premium cotton, regular fit, button-down collar, perfect for formal occasions and business meetings. Available in sizes S to XXL.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Dress%20Shirt%20-%20White&imgurl=https%3A%2F%2Fimage.made-in-china.com%2F202f0j00VqOiHRDPheYv%2FBusiness-Men-Slim-Fit-Formal-White-Shirt-Men-s-Luxury-Long-Sleeve-Shirt.webp&imgrefurl=https%3A%2F%2Fjzf-apparel.en.made-in-china.com%2Fproduct%2FCZMfObyLkUGi%2FChina-Business-Men-Slim-Fit-Formal-White-Shirt-Men-s-Luxury-Long-Sleeve-Shirt.html&docid=N6Kg6D_eXIX1EM&tbnid=Ip1v036dB2I1sM&vet=12ahUKEwjPnKq187eQAxViHhAIHVS1KdUQM3oECBkQAA..i&w=550&h=550&hcb=2&ved=2ahUKEwjPnKq187eQAxViHhAIHVS1KdUQM3oECBkQAA",
        "Price__c": 34.99
    },
    {
        "Name": "Men's Casual Shirt - Blue Check",
        "ProductCode": "SHIRT002",
        "Family": "Clothing",
        "Color__c": "Blue/White",
        "Size__c": "S-XXL",
        "Description": "Stylish blue check casual shirt with comfortable cotton fabric, button-front design, chest pocket, and versatile pattern that pairs well with jeans or chinos.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Casual%20Shirt%20-%20Blue%20Check&imgurl=https%3A%2F%2Fwww.affordable.pk%2Fuploads%2Fproducts%2Fthumbs%2Flarge_15556875520_blue_f.jpg&imgrefurl=https%3A%2F%2Fwww.affordable.pk%2Fitem%2Fmen-clothes-casual-wear-blue-check-casual-shirt-for-men-s-other-14196&docid=g4ZGGEPxHTOaXM&tbnid=zzxZBrpD4FLNKM&vet=12ahUKEwi85JDF87eQAxXGAxAIHVJjOFcQM3oECBsQAA..i&w=1024&h=1280&hcb=2&ved=2ahUKEwi85JDF87eQAxXGAxAIHVJjOFcQM3oECBsQAA",
        "Price__c": 29.99
    },
    {
        "Name": "Men's Oxford Shirt - Light Blue",
        "ProductCode": "SHIRT003",
        "Family": "Clothing",
        "Color__c": "Light Blue",
        "Size__c": "S-XXL",
        "Description": "Premium light blue oxford shirt with button-down collar, durable oxford cloth fabric, perfect for business casual or weekend wear. Classic styling with modern fit.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Oxford%20Shirt%20-%20Light%20Blue&imgurl=https%3A%2F%2Fxcdn.next.co.uk%2Fcommon%2Fitems%2Fdefault%2Fdefault%2Fitemimages%2F3_4Ratio%2Fproduct%2Flge%2F213989s.jpg%3Fim%3DResize%2Cwidth%3D750&imgrefurl=https%3A%2F%2Fwww.nextdirect.com%2Fpk%2Fen%2Fstyle%2Fsu029915%2F213989&docid=htLC008vGlAQfM&tbnid=UqGDTI4vmuPEIM&vet=12ahUKEwi1277W87eQAxXqU1UIHeg4DWUQM3oECBoQAA..i&w=750&h=1000&hcb=2&ved=2ahUKEwi1277W87eQAxXqU1UIHeg4DWUQM3oECBoQAA",
        "Price__c": 39.99
    },
    {
        "Name": "Men's Flannel Shirt - Red Black",
        "ProductCode": "SHIRT004",
        "Family": "Clothing",
        "Color__c": "Red/Black",
        "Size__c": "S-XXL",
        "Description": "Warm red and black flannel shirt made from soft brushed cotton, perfect for cooler weather. Features a classic plaid pattern and comfortable relaxed fit.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Flannel%20Shirt%20-%20Red%20Black&imgurl=https%3A%2F%2Fwww.gruntstyle.com%2Fcdn%2Fshop%2Fproducts%2FBlankPoster_2000X2000_GS3561-GruntStyleBuffaloPlaidFlannel-5.jpg%3Fv%3D1758133768%26width%3D2000&imgrefurl=https%3A%2F%2Fwww.gruntstyle.com%2Fproducts%2Fgrunt-style-buffalo-plaid-flannel%3Fsrsltid%3DAfmBOop5XIClaC9PXKm4lzHRqdarvflgRjQAvvnYsx8pgilTHU1YLv8u&docid=8l5zAfTp69GfZM&tbnid=-BbkHpSsbq7nCM&vet=12ahUKEwjrwN3n87eQAxVgLRAIHStZAb0QM3oECBYQAA..i&w=1000&h=1000&hcb=2&ved=2ahUKEwjrwN3n87eQAxVgLRAIHStZAb0QM3oECBYQAA",
        "Price__c": 32.99
    },
    {
        "Name": "Men's Polo Shirt - Navy Blue",
        "ProductCode": "SHIRT005",
        "Family": "Clothing",
        "Color__c": "Navy Blue",
        "Size__c": "S-XXL",
        "Description": "Classic navy blue polo shirt made from breathable pique cotton, ribbed collar, three-button placket, and comfortable fit for casual or smart casual occasions.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Polo%20Shirt%20-%20Navy%20Blue&imgurl=https%3A%2F%2Fwww.hueman.pk%2Fcdn%2Fshop%2Fproducts%2FNavyBlueMen_sPoloShirt2_f56fa582-5f21-4bfb-98b8-222510ba304c.jpg%3Fv%3D1754376403%26width%3D1445&imgrefurl=https%3A%2F%2Fwww.hueman.pk%2Fproducts%2Fnavy-blue-men-s-polo-shirt&docid=cyhOLlJOL4FByM&tbnid=BhouolngdQYFXM&vet=12ahUKEwiZk9D187eQAxUyJBAIHZIaA4wQM3oECBYQAA..i&w=900&h=1200&hcb=2&ved=2ahUKEwiZk9D187eQAxUyJBAIHZIaA4wQM3oECBYQAA",
        "Price__c": 24.99
    },
    {
"Name": "Men's Button-Down Shirt - White",
"ProductCode": "SHIRT001",
"Family": "Apparel",
"Color__c": "White",
"Size__c": "S-XXL",
"Description": "Crisp white button-down shirt made from cotton, long sleeves, regular fit, wrinkle-resistant, sizes S-XXL, essential for professional or casual looks.",
"Image_URL__c": "https://m.media-amazon.com/images/I/71CoJzdS-ML._AC_UY1000_.jpg",
"Price__c": 49.99
},
{
"Name": "Men's Polo Shirt - Navy",
"ProductCode": "SHIRT002",
"Family": "Apparel",
"Color__c": "Navy",
"Size__c": "M-XXL",
"Description": "Navy polo shirt with short sleeves, moisture-wicking fabric, classic collar, sizes M-XXL, comfortable for sports or casual wear.",
"Image_URL__c": "https://i5.walmartimages.com/seo/Victory-Outfitters-Men-s-Breathable-Performance-Polo-Shirt-Navy-XXL_1bf67e1e-1cb2-44b2-8b75-8c38c8c7052c.6a3da98ff654556dcafb129e34b442de.jpeg",
"Price__c": 39.99
},
{
"Name": "Men's Flannel Shirt - Red Plaid",
"ProductCode": "SHIRT003",
"Family": "Apparel",
"Color__c": "Red Plaid",
"Size__c": "S-XL",
"Description": "Cozy red plaid flannel shirt with button front, soft cotton material, long sleeves, sizes S-XL, great for layering in cooler weather.",
"Image_URL__c": "https://www.vermontflannel.com/cdn/shop/files/VFC_Mens-Classic_Red-Buffalo_Model-Silo_1_Crop.jpg?v=1755886451&width=1445",
"Price__c": 44.99
},
{
"Name": "Men's T-Shirt - White",
"ProductCode": "SHIRT004",
"Family": "Apparel",
"Color__c": "White",
"Size__c": "S-XXL",
"Description": "Classic white t-shirt with crew neck, soft cotton fabric, regular fit, sizes S-XXL, essential wardrobe staple.",
"Image_URL__c": "https://hips.hearstapps.com/hmg-prod/images/mhl-052224-hanes-1264-socialindex-6661f22b2f322.jpg?crop=0.412xw:0.824xh;0.301xw,0&resize=1120:*",
"Price__c": 19.99
},
{
"Name": "Men's Henley Shirt - Blue",
"ProductCode": "SHIRT005",
"Family": "Apparel",
"Color__c": "Blue",
"Size__c": "M-XXL",
"Description": "Blue henley shirt with button placket, long sleeves, textured fabric, sizes M-XXL, comfortable for casual wear.",
"Image_URL__c": "https://www.american-giant.com/cdn/shop/files/M2-9M-5-PAGB_10344.jpg?v=1729800043&w=3000",
"Price__c": 39.99
},
{
"Name": "Men's Dress Shirt - Pink",
"ProductCode": "SHIRT006",
"Family": "Apparel",
"Color__c": "Pink",
"Size__c": "S-XL",
"Description": "Pink dress shirt with wrinkle-resistant fabric, button-down collar, slim fit, sizes S-XL, suitable for formal events.",
"Image_URL__c": "http://ashanderie.com/cdn/shop/files/dress-shirts-pink-dress-shirt-46718451876138.jpg?v=1727823507",
"Price__c": 49.99
},

    # ===== NEW: Jackets =====
    {
        "Name": "Men's Leather Jacket - Black",
        "ProductCode": "JACKET001",
        "Family": "Clothing",
        "Color__c": "Black",
        "Size__c": "S-XXL",
        "Description": "Classic black leather jacket made from genuine leather, featuring zipper front, multiple pockets, and comfortable lining. Timeless style that never goes out of fashion.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Leather%20Jacket%20-%20Black&imgurl=https%3A%2F%2Fwww.thejacketmaker.pk%2Fcdn%2Fshop%2Ffiles%2FIonic_Black_Leather_Jacket_With_Minimalist_Design_made_of_100_Real_Leather_in_matte_black_finish_1_821aa6f2-e2d8-4b7b-9144-c9311b10ed8a_2048x.jpg%3Fv%3D1760634233&imgrefurl=https%3A%2F%2Fwww.thejacketmaker.pk%2Fcollections%2Fmens-leather-jackets&docid=NFHylUkk3-9RDM&tbnid=9QO3N0X2KvIsMM&vet=12ahUKEwiA4M-a9LeQAxXGgSoKHWmaMFsQM3oECBcQAA..i&w=1000&h=1000&hcb=2&ved=2ahUKEwiA4M-a9LeQAxXGgSoKHWmaMFsQM3oECBcQAA",
        "Price__c": 199.99
    },
    {
        "Name": "Men's Denim Jacket - Blue",
        "ProductCode": "JACKET002",
        "Family": "Clothing",
        "Color__c": "Blue",
        "Size__c": "S-XXL",
        "Description": "Classic blue denim jacket with durable cotton construction, button-front design, chest pockets, and versatile styling that layers well over shirts or sweaters.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Denim%20Jacket%20-%20Blue&imgurl=https%3A%2F%2F5.imimg.com%2Fdata5%2FSELLER%2FDefault%2F2022%2F10%2FPU%2FFH%2FRY%2F162001345%2Fmen-cotton-t-shirt-500x500.jpg&imgrefurl=https%3A%2F%2Fwww.indiamart.com%2Fproddetail%2Fmen-denim-jacket-27373113712.html%3Fsrsltid%3DAfmBOorPprBW_PIHVpNC35UojHArSqrBu9BGvUefSzyV6PTVkvQYidmH&docid=huBAATqzsF9NDM&tbnid=tS4jWv_0jyTnpM&vet=12ahUKEwiwguy09LeQAxXtGhAIHe5yB0UQM3oECBUQAA..i&w=500&h=500&hcb=2&ved=2ahUKEwiwguy09LeQAxXtGhAIHe5yB0UQM3oECBUQAA",
        "Price__c": 59.99
    },
    {
        "Name": "Men's Bomber Jacket - Green",
        "ProductCode": "JACKET003",
        "Family": "Clothing",
        "Color__c": "Green",
        "Size__c": "S-XXL",
        "Description": "Stylish green bomber jacket with ribbed cuffs and hem, zipper front, multiple pockets, and lightweight insulation perfect for spring and fall weather.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Bomber%20Jacket%20-%20Green&imgurl=https%3A%2F%2Fm.media-amazon.com%2Fimages%2FI%2F51ylk6F0rfL._AC_SL1000_.jpg&imgrefurl=https%3A%2F%2Fwww.ubuy.com.pk%2Fen%2Fproduct%2F127ZK0C8-mens-lightweight-bomber-jackets-fall-winter-outerwear-full-zip-up-baseball-varsity-jacket%3Fsrsltid%3DAfmBOormFz9PMnbukZENrBvJKLph-011-NvLsnx7OV1y9c6cMz5d_fG3&docid=HlOkrXmJfSm_XM&tbnid=fie5cLydxsa8DM&vet=12ahUKEwi8m63H9LeQAxWOKxAIHc4yAr8QM3oECBcQAA..i&w=721&h=1000&hcb=2&ved=2ahUKEwi8m63H9LeQAxWOKxAIHc4yAr8QM3oECBcQAA",
        "Price__c": 79.99
    },
    {
        "Name": "Men's Rain Jacket - Yellow",
        "ProductCode": "JACKET004",
        "Family": "Clothing",
        "Color__c": "Yellow",
        "Size__c": "S-XXL",
        "Description": "Waterproof yellow rain jacket with sealed seams, adjustable hood, multiple pockets, and breathable fabric. Perfect protection against wet weather conditions.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Rain%20Jacket%20-%20Yellow&imgurl=https%3A%2F%2Fkieljamespatrick.com%2Fcdn%2Fshop%2Fproducts%2FOld-Salt-on-Kiel-for-Site_1600x.jpg%3Fv%3D1707321694&imgrefurl=https%3A%2F%2Fkieljamespatrick.com%2Fproducts%2Fold-salt-raincoat-mens%3Fsrsltid%3DAfmBOorTi4OPOEcHVtCNGHxgzdMdqlYW9kQzOyT4BDbAtNj5KyDN_8AO&docid=g2-Lals181ShZM&tbnid=y6dolcHAT2osmM&vet=12ahUKEwjFgeTW9LeQAxWiERAIHQqXKd4QM3oECCAQAA..i&w=1600&h=2400&hcb=2&ved=2ahUKEwjFgeTW9LeQAxWiERAIHQqXKd4QM3oECCAQAA",
        "Price__c": 69.99
    },
    {
        "Name": "Men's Blazer - Navy Blue",
        "ProductCode": "JACKET005",
        "Family": "Clothing",
        "Color__c": "Navy Blue",
        "Size__c": "S-XXL",
        "Description": "Elegant navy blue blazer with notch lapel, two-button closure, and premium wool blend fabric. Perfect for business meetings, weddings, or formal events.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Blazer%20-%20Navy%20Blue&imgurl=https%3A%2F%2Fandreemilio.com%2Fwp-content%2Fuploads%2F2019%2F04%2FNavy-Blue-Slim-Fit-Blazer.jpg&imgrefurl=https%3A%2F%2Fandreemilio.com%2Fproduct%2Fnavy-blue-mens-blazer%2F%3Fsrsltid%3DAfmBOoq0uIycNVjw_YJHSR5Nd1hae8GWwCzP6PbYr9I3PM9XdXcRZq4R&docid=xWXhQj6uGOMDaM&tbnid=zEfqV6ST2nJZ8M&vet=12ahUKEwjZ_-jo9LeQAxV1IhAIHWo7GA0QM3oECBcQAA..i&w=1000&h=1000&hcb=2&ved=2ahUKEwjZ_-jo9LeQAxV1IhAIHWo7GA0QM3oECBcQAA",
        "Price__c": 129.99
    },
    {
"Name": "Men's Leather Jacket - Black",
"ProductCode": "JACKET001",
"Family": "Apparel",
"Color__c": "Black",
"Size__c": "M-XXL",
"Description": "Stylish black leather jacket with zip front, multiple pockets, durable construction, sizes M-XXL, perfect for casual or edgy outfits.",
"Image_URL__c": "https://thursdayboots.com/cdn/shop/files/1024x1024-Mens-Keanu-Black-010924-1_1024x1024.jpg?v=1705095642",
"Price__c": 149.99
},
{
"Name": "Men's Bomber Jacket - Green",
"ProductCode": "JACKET002",
"Family": "Apparel",
"Color__c": "Green",
"Size__c": "S-XXL",
"Description": "Classic green bomber jacket with ribbed cuffs, zip closure, lightweight lining, sizes S-XXL, versatile for everyday wear.",
"Image_URL__c": "https://ashanderie.com/cdn/shop/files/bomber-jacket-dark-green-bomber-jacket-44753482154282.jpg?v=1714535716&width=1080",
"Price__c": 99.99
},
{
"Name": "Men's Denim Jacket - Blue",
"ProductCode": "JACKET003",
"Family": "Apparel",
"Color__c": "Blue",
"Size__c": "M-XXL",
"Description": "Classic blue denim jacket with button front, chest pockets, durable cotton, sizes M-XXL, timeless style for casual looks.",
"Image_URL__c": "https://m.media-amazon.com/images/I/91mkkg7dORL._AC_UY1000_.jpg",
"Price__c": 79.99
},
{
"Name": "Men's Windbreaker - Red",
"ProductCode": "JACKET004",
"Family": "Apparel",
"Color__c": "Red",
"Size__c": "S-XXL",
"Description": "Lightweight red windbreaker with zip front, hood, water-resistant, sizes S-XXL, ideal for outdoor activities in windy weather.",
"Image_URL__c": "http://o8lifestyle.com/cdn/shop/files/M51138_08_RED_008_1200x1800_d099e6ec-93ac-41e8-b5c3-be467f8e4b07.jpg?v=1693517064&width=2048",
"Price__c": 59.99
},

    # ===== NEW: Socks =====
    {
        "Name": "Men's Dress Socks - Black",
        "ProductCode": "SOCK001",
        "Family": "Accessories",
        "Color__c": "Black",
        "Size__c": "One Size",
        "Description": "Premium black dress socks made from combed cotton with reinforced heel and toe. Comfortable elastic band and breathable fabric perfect for all-day wear.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Dress%20Socks%20-%20Black&imgurl=https%3A%2F%2Fcdn.shopify.com%2Fs%2Ffiles%2F1%2F0505%2F7019%2F9217%2Fproducts%2FX022_l.jpg%3Fv%3D1613766050&imgrefurl=https%3A%2F%2Fwww.thetiebar.com%2Fproduct%2Fsck-3594-0001%3Fsrsltid%3DAfmBOoqI4vYm2HhJcusDG7XNz67dXVHG7kkmqjWVQWDPr7Zx5DwSxO7J&docid=LD76Ta1UdhwMOM&tbnid=ec93-q2Ip4kFNM&vet=12ahUKEwiF3__u9beQAxWOFxAIHTcYHIUQM3oECBUQAA..i&w=700&h=817&hcb=2&ved=2ahUKEwiF3__u9beQAxWOFxAIHTcYHIUQM3oECBUQAA",
        "Price__c": 12.99
    },
    {
        "Name": "Men's Athletic Socks - White",
        "ProductCode": "SOCK002",
        "Family": "Accessories",
        "Color__c": "White",
        "Size__c": "9-12",
        "Description": "Comfortable white athletic socks with cushioned sole, moisture-wicking fabric, and arch support. Perfect for sports, gym workouts, or everyday active wear.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Athletic%20Socks%20-%20White&imgurl=https%3A%2F%2Fm.media-amazon.com%2Fimages%2FI%2F71d6hcDT5NL._AC_UY1000_.jpg&imgrefurl=https%3A%2F%2Fwww.amazon.com%2FMUQU-Mens-White-Crew-Socks%2Fdp%2FB0DKWVS25K&docid=-1yxDPfNgRc9iM&tbnid=VlRJUlR-xQuPcM&vet=12ahUKEwiO54f99beQAxVeTlUIHUTTOdYQM3oECBgQAA..i&w=1000&h=1000&hcb=2&ved=2ahUKEwiO54f99beQAxVeTlUIHUTTOdYQM3oECBgQAA",
        "Price__c": 14.99
    },
    {
        "Name": "Men's Casual Socks - Navy Blue",
        "ProductCode": "SOCK003",
        "Family": "Accessories",
        "Color__c": "Navy Blue",
        "Size__c": "One Size",
        "Description": "Soft navy blue casual socks with comfortable fit, breathable cotton blend, and subtle pattern. Perfect for everyday wear with jeans or casual pants.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Casual%20Socks%20-%20Navy%20Blue&imgurl=https%3A%2F%2Fxcdn.next.co.uk%2Fcommon%2Fitems%2Fdefault%2Fdefault%2Fitemimages%2F3_4Ratio%2Fproduct%2Flge%2FC64696s.jpg%3Fim%3DResize%2Cwidth%3D750&imgrefurl=https%3A%2F%2Fwww.nextdirect.com%2Fpk%2Fen%2Fstyle%2Fst366311%2Fc64696&docid=wVZ2aXgKlHdaQM&tbnid=af0eRcloyy10_M&vet=12ahUKEwidj4aR9reQAxUjEBAIHQ_fCnQQM3oECBoQAA..i&w=750&h=1000&hcb=2&ved=2ahUKEwidj4aR9reQAxUjEBAIHQ_fCnQQM3oECBoQAA",
        "Price__c": 11.99
    },
    {
        "Name": "Men's Ankle Socks - Gray",
        "ProductCode": "SOCK004",
        "Family": "Accessories",
        "Color__c": "Gray",
        "Size__c": "9-12",
        "Description": "Low-cut gray ankle socks with no-show design, perfect for wearing with sneakers or loafers. Moisture-wicking fabric and comfortable elastic band.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Ankle%20Socks%20-%20Gray&imgurl=https%3A%2F%2Fkxadmin.metroshoes.com%2Fproduct%2F20-8274%2F250%2F20-8274M14.jpg&imgrefurl=https%3A%2F%2Fwww.metroshoes.com%2Fmetro-20-8274-grey-socks.html&docid=m4tNofZjFKw15M&tbnid=bnaPtxVrAwX2rM&vet=12ahUKEwjOjsqq9reQAxX8KRAIHU_lCF8QM3oECBYQAA..i&w=250&h=250&hcb=2&ved=2ahUKEwjOjsqq9reQAxX8KRAIHU_lCF8QM3oECBYQAA",
        "Price__c": 13.99
    },
    {
        "Name": "Men's Wool Socks - Brown",
        "ProductCode": "SOCK005",
        "Family": "Accessories",
        "Color__c": "Brown",
        "Size__c": "10-13",
        "Description": "Warm brown wool socks with thermal insulation, perfect for cold weather or outdoor activities. Soft merino wool blend that's comfortable and durable.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Wool%20Socks%20-%20Brown&imgurl=https%3A%2F%2Fcdn.shopify.com%2Fs%2Ffiles%2F1%2F0267%2F6254%2F3149%2Fproducts%2Fsop4200306_3.jpg%3Fv%3D1608146180&imgrefurl=https%3A%2F%2Fturnbullandasser.co.uk%2Fproducts%2Fchocolate-brown-mid-length-merino-wool-socks&docid=okSER-F8R6aB2M&tbnid=wq0lyhctcxuCUM&vet=12ahUKEwi9g4m39reQAxWFORAIHV24CycQM3oECBcQAA..i&w=1600&h=1600&hcb=2&ved=2ahUKEwi9g4m39reQAxWFORAIHV24CycQM3oECBcQAA",
        "Price__c": 16.99
    },
    {
"Name": "Men's Crew Socks - Black",
"ProductCode": "SOCK001",
"Family": "Accessories",
"Color__c": "Black",
"Size__c": "One Size",
"Description": "Comfortable black crew socks with cushioned soles, moisture-wicking fabric, reinforced heels, one size fits most, ideal for daily wear or sports.",
"Image_URL__c": "http://www.gymreapers.com/cdn/shop/files/PHO09667_1.jpg?v=1700785582&width=2048",
"Price__c": 14.99
},
{
"Name": "Men's Dress Socks - Grey",
"ProductCode": "SOCK002",
"Family": "Accessories",
"Color__c": "Grey",
"Size__c": "One Size",
"Description": "Elegant grey dress socks with ribbed design, soft cotton blend, mid-calf length, one size fits most, perfect for formal attire.",
"Image_URL__c": "https://boardroomsocks.com/cdn/shop/products/GreyPimaCottonMid-CalfDressSocksonModel_7ef2f973-40d1-4a15-ba5a-7d575c04d1c7_1200x.jpg?v=1623074420",
"Price__c": 12.99
},
{
"Name": "Men's Ankle Socks - White",
"ProductCode": "SOCK003",
"Family": "Accessories",
"Color__c": "White",
"Size__c": "One Size",
"Description": "Comfortable white ankle socks with cushioned heel, breathable material, one size fits most, perfect for sports and casual wear.",
"Image_URL__c": "https://m.media-amazon.com/images/I/514gNw2T+CL._AC_UY1000_.jpg",
"Price__c": 14.99
},
{
"Name": "Men's No Show Socks - Black",
"ProductCode": "SOCK004",
"Family": "Accessories",
"Color__c": "Black",
"Size__c": "One Size",
"Description": "Invisible black no show socks with silicone grip, soft fabric, one size fits most, ideal for loafers and sneakers.",
"Image_URL__c": "https://unboundmerino.com/cdn/shop/files/unbound-merino-merino-no-show-socks-3.jpg?crop=center&height=650&v=1707458911&width=541",
"Price__c": 12.99
},

    # ===== Additional Products =====
    {
        "Name": "Men's Luxury Watch - Rose Gold",
        "ProductCode": "WATCH011",
        "Family": "Watches",
        "Color__c": "Rose Gold",
        "Size__c": "42mm",
        "Description": "Elegant rose gold luxury watch with genuine leather strap, sapphire crystal glass, and automatic movement. Water resistant up to 100 meters.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Luxury%20Watch%20-%20Rose%20Gold&imgurl=https%3A%2F%2Fm.media-amazon.com%2Fimages%2FI%2F71gg1F-A5BL._AC_SL1500_.jpg&imgrefurl=https%3A%2F%2Fwww.ubuy.com.pk%2Fen%2Fproduct%2F1YRY8FSU-oblvlo-luxury-rose-gold-watches-men-39-s-skeleton-dial-automatic-watches-leather-strap-vm-1%3Fsrsltid%3DAfmBOophz4nvdAZVNkfwooKKXs4uM4O4t9DkYC3a-0a5V15YvBKR1Hyt&docid=9chIXzDRVeTZoM&tbnid=S8sdinh6AQMuOM&vet=12ahUKEwj6zpnK9reQAxXDHRAIHWygOzoQM3oECBgQAA..i&w=955&h=1500&hcb=2&ved=2ahUKEwj6zpnK9reQAxXDHRAIHWygOzoQM3oECBgQAA",
        "Price__c": 249.99
    },
    {
        "Name": "Men's Sports Shoes - Black/Red",
        "ProductCode": "SHOE011",
        "Family": "Footwear",
        "Color__c": "Black/Red",
        "Size__c": "7-12",
        "Description": "Performance sports shoes with breathable mesh upper, responsive cushioning, and durable rubber outsole. Perfect for running and gym workouts.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Sports%20Shoes%20-%20Black%2FRed&imgurl=https%3A%2F%2Fd30fs77zq6vq2v.cloudfront.net%2Fproduct%2F1080x1619%2F19122023%2Fpu-224-red-black-1_1699338590-735280502008.jpg&imgrefurl=https%3A%2F%2Fwww.clicky.pk%2Fmen-premium-black-red-sports-shoes-red%3Fid%3D657397f3baf109496484693a&docid=AywSptjPeD2weM&tbnid=_bMklE4I_71pkM&vet=12ahUKEwjXh5Td9reQAxUtKRAIHZHpKMAQM3oECBwQAA..i&w=1080&h=1619&hcb=2&ved=2ahUKEwjXh5Td9reQAxUtKRAIHZHpKMAQM3oECBwQAA",
        "Price__c": 79.99
    },
    {
        "Name": "Men's Formal Trousers - Charcoal Gray",
        "ProductCode": "TROUSER011",
        "Family": "Clothing",
        "Color__c": "Charcoal Gray",
        "Size__c": "30-42",
        "Description": "Elegant charcoal gray formal trousers with premium wool blend fabric, perfect for business meetings and formal occasions. Available in multiple sizes.",
        "Image_URL__c": "https://www.google.com/imgres?q=Men%27s%20Formal%20Trousers%20-%20Charcoal%20Gray&imgurl=https%3A%2F%2Fcharcoal.com.pk%2Fcdn%2Fshop%2Ffiles%2FDSC03622.webp%3Fv%3D1760525140%26width%3D2646&imgrefurl=https%3A%2F%2Fcharcoal.com.pk%2Fcollections%2Fdress-pants%3Fsrsltid%3DAfmBOoqtvTpIf7lbi8AIZ-HNQJpdVdPRAiVVGBnR-BihWdWABIjEoJf9&docid=veKDD7iYl8QQsM&tbnid=ad5FDtPfDUHzTM&vet=12ahUKEwj79IHs9reQAxWTNxAIHXQqAQAQM3oECBwQAA..i&w=2646&h=4234&hcb=2&ved=2ahUKEwj79IHs9reQAxWTNxAIHXQqAQAQM3oECBwQAA",
        "Price__c": 64.99
    }
]

# --- Upload products + create pricebook entries ---
created = []
for product in products:
    try:
        # ✅ Clean long Google redirect image URLs
        product["Image_URL__c"] = clean_image_url(product["Image_URL__c"])

        # Check if product already exists
        existing = sf.query(f"SELECT Id FROM Product2 WHERE ProductCode = '{product['ProductCode']}' LIMIT 1")

        if existing["records"]:
            product_id = existing["records"][0]["Id"]
            print(f"⚙️ Product already exists, updating: {product['Name']}")
            sf.Product2.update(product_id, product)
        else:
            result = sf.Product2.create(product)
            product_id = result["id"]
            print(f"✅ Created product: {product['Name']} ({product['ProductCode']})")

        # Create or update pricebook entry
        price_entry = sf.query(f"""
            SELECT Id FROM PricebookEntry
            WHERE Pricebook2Id = '{pricebook_id}' AND Product2Id = '{product_id}' LIMIT 1
        """)

        if price_entry["records"]:
            print(f"🔁 PricebookEntry already exists for {product['Name']}")
        else:
            sf.PricebookEntry.create({
                "Pricebook2Id": pricebook_id,
                "Product2Id": product_id,
                "UnitPrice": product["Price__c"],
                "IsActive": True
            })
            print(f"💲 Added PricebookEntry for {product['Name']} at ${product['Price__c']}")

        created.append(product["Name"])

    except Exception as e:
        print(f"⚠️ Error processing {product['Name']}: {e}")

print(f"\n🎉 Successfully added or updated {len(created)} products to Salesforce (with pricebook entries)!")