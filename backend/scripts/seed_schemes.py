"""
Seed the government_schemes collection with common Indian agricultural schemes.
Usage: python scripts/seed_schemes.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


SCHEMES = [
    {
        "scheme_name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "scheme_type": "income_support",
        "description": "Direct income support of ₹6,000 per year to farmer families.",
        "benefits": "₹6,000 per year in 3 equal installments of ₹2,000 directly to bank account.",
        "eligibility_criteria": "All landholding farmer families across India. Excludes institutional land holders, farmer families holding constitutional posts, serving/retired government employees, income tax payers.",
        "application_process": "Register on PM-KISAN portal or through Common Service Centers (CSC).",
        "documents_required": ["Aadhaar card", "Bank account details", "Land records"],
        "target_states": [],
        "target_crops": [],
        "max_land_acres": None,
        "min_land_acres": 0.0,
        "application_url": "https://pmkisan.gov.in",
        "is_active": True,
    },
    {
        "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "scheme_type": "crop_insurance",
        "description": "Comprehensive crop insurance covering pre-sowing to post-harvest losses.",
        "benefits": "Crop insurance at low premiums: 2% for Kharif, 1.5% for Rabi, 5% for commercial/horticultural crops.",
        "eligibility_criteria": "All farmers growing notified crops in notified areas. Compulsory for loanee farmers, voluntary for others.",
        "application_process": "Apply through nearest bank, Common Service Centre, or online portal during crop season.",
        "documents_required": ["Land records (7/12 extract)", "Bank passbook", "Sowing certificate", "Aadhaar card"],
        "target_states": [],
        "target_crops": [],
        "max_land_acres": None,
        "min_land_acres": 0.0,
        "application_url": "https://pmfby.gov.in",
        "is_active": True,
    },
    {
        "scheme_name": "Kisan Credit Card (KCC)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "scheme_type": "credit",
        "description": "Short-term credit for crop cultivation, post-harvest, allied activities.",
        "benefits": "Revolving credit up to ₹3 lakh at 7% interest (4% effective after interest subvention). Higher limits based on land holding.",
        "eligibility_criteria": "Farmers, tenant farmers, oral lessees, sharecroppers, SHG/JLG members involved in agriculture.",
        "application_process": "Apply at nearest bank branch, RRB, or cooperative bank with land records.",
        "documents_required": ["Application form", "Identity proof", "Address proof", "Land records", "Passport photo"],
        "target_states": [],
        "target_crops": [],
        "max_land_acres": None,
        "min_land_acres": 0.0,
        "application_url": "https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx",
        "is_active": True,
    },
    {
        "scheme_name": "Soil Health Card Scheme",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "scheme_type": "soil_health",
        "description": "Free soil testing and health cards showing soil nutrient status and recommendations.",
        "benefits": "Free soil testing every 2 years. Soil Health Card with crop-wise recommendations for nutrients and fertilizers.",
        "eligibility_criteria": "All farmers across India.",
        "application_process": "Contact nearest Krishi Vigyan Kendra (KVK) or state agriculture department for soil testing.",
        "documents_required": ["Aadhaar card", "Land records"],
        "target_states": [],
        "target_crops": [],
        "max_land_acres": None,
        "min_land_acres": 0.0,
        "application_url": "https://soilhealth.dac.gov.in",
        "is_active": True,
    },
    {
        "scheme_name": "PM Kisan Maan Dhan Yojana (PM-KMY)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "scheme_type": "pension",
        "description": "Voluntary pension scheme for small and marginal farmers.",
        "benefits": "₹3,000/month pension after age 60. Equal contribution by farmer and government.",
        "eligibility_criteria": "Small and marginal farmers aged 18-40 years with landholding up to 2 hectares.",
        "application_process": "Enroll at Common Service Centres (CSC) with Aadhaar and savings bank account.",
        "documents_required": ["Aadhaar card", "Savings bank account / Jan-Dhan account", "Land records"],
        "target_states": [],
        "target_crops": [],
        "max_land_acres": 4.94,
        "min_land_acres": 0.0,
        "application_url": "https://maandhan.in",
        "is_active": True,
    },
    {
        "scheme_name": "National Mission for Sustainable Agriculture (NMSA)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "scheme_type": "sustainability",
        "description": "Enhancing agricultural productivity through climate change adaptation.",
        "benefits": "Subsidies for drip/sprinkler irrigation, soil health management, organic farming, watershed development.",
        "eligibility_criteria": "All farmers. Special priority to small/marginal farmers and rainfed areas.",
        "application_process": "Apply through district agriculture office or state nodal agency.",
        "documents_required": ["Aadhaar card", "Land records", "Bank account"],
        "target_states": [],
        "target_crops": [],
        "max_land_acres": None,
        "min_land_acres": 0.0,
        "application_url": "https://nmsa.dac.gov.in",
        "is_active": True,
    },
    {
        "scheme_name": "Paramparagat Krishi Vikas Yojana (PKVY)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "scheme_type": "organic_farming",
        "description": "Promotion of organic farming through cluster approach.",
        "benefits": "₹50,000 per hectare over 3 years for cluster formation, organic inputs, certification, marketing.",
        "eligibility_criteria": "Farmer clusters of minimum 50 farmers covering 50 acres. Traditional/tribal farming communities prioritized.",
        "application_process": "Form a farmer group and apply through district agriculture department.",
        "documents_required": ["Group formation documents", "Land records", "Bank account"],
        "target_states": [],
        "target_crops": [],
        "max_land_acres": None,
        "min_land_acres": 0.0,
        "application_url": "https://pgsindia-ncof.gov.in",
        "is_active": True,
    },
]


async def seed():
    import os
    os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
    os.environ.setdefault("MONGO_DB_NAME", "krishi_sahayak")

    from db.mongodb import connect_db
    from models.scheme import GovernmentScheme

    await connect_db()

    inserted = 0
    for data in SCHEMES:
        existing = await GovernmentScheme.find_one(
            GovernmentScheme.scheme_name == data["scheme_name"]
        )
        if existing:
            print(f"  Already exists: {data['scheme_name']}")
            continue

        scheme = GovernmentScheme(**data)
        await scheme.insert()
        print(f"  Inserted: {data['scheme_name']}")
        inserted += 1

    print(f"\nDone. Inserted {inserted} new schemes.")


if __name__ == "__main__":
    asyncio.run(seed())
