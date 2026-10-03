import os
from PIL import Image, ImageDraw, ImageFont

def generate_samples(output_dir: str = "sample_data"):
    os.makedirs(output_dir, exist_ok=True)
    font = ImageFont.load_default()

    # 1. SBI KYC Fraud Screenshot (Red alert header, banking impersonation, phishing link)
    img1 = Image.new("RGB", (480, 320), color=(245, 247, 250))
    d1 = ImageDraw.Draw(img1)
    # Red urgency header
    d1.rectangle([(0, 0), (480, 60)], fill=(210, 35, 45))
    d1.text((20, 20), "ALERT: SBI NETBANKING SUSPENDED", fill=(255, 255, 255), font=font)
    # Body text
    body1 = (
        "Dear Customer,\n\n"
        "Your SBI Account access will be blocked within 24 hours\n"
        "due to incomplete KYC documents.\n\n"
        "Please update your PAN and Aadhaar immediately:\n"
        "http://sbi-netbanking-kyc.icu/pan-update.php\n\n"
        "Do not share your OTP or netbanking password."
    )
    d1.text((30, 80), body1, fill=(30, 30, 30), font=font)
    path1 = os.path.join(output_dir, "sbi_kyc_fraud.png")
    img1.save(path1)

    # 2. International Lottery Winner
    img2 = Image.new("RGB", (480, 300), color=(255, 250, 240))
    d2 = ImageDraw.Draw(img2)
    d2.rectangle([(0, 0), (480, 50)], fill=(230, 160, 20))
    d2.text((20, 18), "*** INTERNATIONAL LOTTERY NOTIFICATION ***", fill=(255, 255, 255), font=font)
    body2 = (
        "CONGRATULATIONS!\n\n"
        "Your mobile number was selected as 1st prize winner of $1,000,000\n"
        "in the Global Mobile Rewards 2026.\n\n"
        "Claim your cash prize now:\n"
        "http://free-gift-card-bonus-claim.buzz/win-iphone-today\n\n"
        "Send your bank account details and $50 transfer fee."
    )
    d2.text((30, 75), body2, fill=(20, 20, 20), font=font)
    path2 = os.path.join(output_dir, "lottery_winner.png")
    img2.save(path2)

    # 3. FedEx Customs Delivery Notice
    img3 = Image.new("RGB", (480, 280), color=(250, 250, 255))
    d3 = ImageDraw.Draw(img3)
    d3.rectangle([(0, 0), (480, 50)], fill=(77, 20, 140))
    d3.text((20, 18), "FedEx Express - Package Status Alert", fill=(255, 255, 255), font=font)
    body3 = (
        "Tracking #: FX-9812739\n"
        "Status: Held at Customs Clearance\n\n"
        "Your shipment requires an import duty settlement of $2.50.\n"
        "Confirm your delivery address and pay pending duty:\n"
        "http://customs-tax-clearance-parcel.top/pay-pending-duty"
    )
    d3.text((30, 70), body3, fill=(30, 30, 30), font=font)
    path3 = os.path.join(output_dir, "fedex_delivery.png")
    img3.save(path3)

    # 4. Clean Benign Invoice
    img4 = Image.new("RGB", (480, 260), color=(255, 255, 255))
    d4 = ImageDraw.Draw(img4)
    d4.rectangle([(0, 0), (480, 45)], fill=(40, 120, 80))
    d4.text((20, 15), "Official Store Receipt - Purchase Confirmed", fill=(255, 255, 255), font=font)
    body4 = (
        "Receipt #: REC-2026-10492\n"
        "Date: October 2026\n"
        "Amount: $45.00 (Paid via Credit Card)\n\n"
        "Thank you for shopping with us.\n"
        "Visit: https://www.amazon.com for order details."
    )
    d4.text((30, 65), body4, fill=(40, 40, 40), font=font)
    path4 = os.path.join(output_dir, "clean_invoice.png")
    img4.save(path4)

    print(f"Generated sample screenshot images in: {output_dir}")

if __name__ == "__main__":
    generate_samples()
