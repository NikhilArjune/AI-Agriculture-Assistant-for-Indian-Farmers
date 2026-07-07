from fastapi import APIRouter, Depends, HTTPException

from core.dependencies import require_farmer
from models.farmer_profile import FarmerProfile
from models.scheme import GovernmentScheme
from models.user import User
from schemas.scheme import SchemeResult, SchemeSearchRequest, SchemeSearchResponse

router = APIRouter(prefix="/schemes", tags=["schemes"])


@router.post("/search", response_model=SchemeSearchResponse)
async def search_schemes(payload: SchemeSearchRequest, current_user: User = Depends(require_farmer)):
    profile = await FarmerProfile.find_one(FarmerProfile.user_id == current_user.id)
    if not profile:
        raise HTTPException(status_code=400, detail="Complete your farmer profile first.")

    query = (payload.query or "").strip()
    state = payload.state or profile.location.state
    crop = payload.crop or (profile.primary_crops[0] if profile.primary_crops else "")

    schemes = await _search_scheme_documents(query=query, state=state, crop=crop)
    if not schemes:
        schemes = _fallback_schemes(query=query, state=state, crop=crop)

    advisory = _build_advisory(query=query, state=state, crop=crop, schemes=schemes)
    return SchemeSearchResponse(
        schemes=schemes,
        advisory_text=advisory,
        sources=["Government scheme database", "Krishi Sahayak fallback catalogue"],
    )


async def _search_scheme_documents(query: str, state: str, crop: str) -> list[SchemeResult]:
    docs = await GovernmentScheme.find(GovernmentScheme.is_active == True).limit(50).to_list()
    terms = [term.lower() for term in f"{query} {state} {crop}".split() if term.strip()]
    results: list[tuple[int, GovernmentScheme]] = []

    for doc in docs:
        haystack = " ".join(
            [
                doc.scheme_name,
                doc.ministry,
                doc.scheme_type,
                doc.description,
                doc.benefits,
                doc.eligibility_criteria,
                " ".join(doc.target_states),
                " ".join(doc.target_crops),
            ]
        ).lower()
        score = sum(1 for term in terms if term in haystack)
        state_match = not doc.target_states or not state or state.lower() in [s.lower() for s in doc.target_states]
        crop_match = not doc.target_crops or not crop or crop.lower() in [c.lower() for c in doc.target_crops]
        if score > 0 and state_match and crop_match:
            results.append((score, doc))

    results.sort(key=lambda item: item[0], reverse=True)
    return [_to_scheme_result(doc, True) for _, doc in results[:10]]


def _to_scheme_result(doc: GovernmentScheme, is_eligible: bool | None = None) -> SchemeResult:
    return SchemeResult(
        scheme_id=str(doc.id),
        scheme_name=doc.scheme_name,
        ministry=doc.ministry,
        benefits=doc.benefits,
        eligibility_criteria=doc.eligibility_criteria,
        application_url=doc.application_url,
        is_eligible=is_eligible,
    )


def _fallback_schemes(query: str, state: str, crop: str) -> list[SchemeResult]:
    q = query.lower()
    catalogue = [
        SchemeResult(
            scheme_id="pmfby",
            scheme_name="Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            ministry="Ministry of Agriculture and Farmers Welfare",
            benefits="Crop insurance coverage against yield losses caused by natural calamities, pests, and diseases.",
            eligibility_criteria="Farmers growing notified crops in notified areas may apply through banks, CSCs, or the official PMFBY portal.",
            application_url="https://pmfby.gov.in/",
            is_eligible=True,
        ),
        SchemeResult(
            scheme_id="pm-kisan",
            scheme_name="PM-KISAN",
            ministry="Ministry of Agriculture and Farmers Welfare",
            benefits="Income support for eligible landholding farmer families through direct benefit transfer.",
            eligibility_criteria="Eligible farmer families with cultivable land, subject to exclusion criteria.",
            application_url="https://pmkisan.gov.in/",
            is_eligible=None,
        ),
        SchemeResult(
            scheme_id="kcc",
            scheme_name="Kisan Credit Card (KCC)",
            ministry="Department of Agriculture and Farmers Welfare",
            benefits="Short-term credit support for crop cultivation, allied activities, and working capital needs.",
            eligibility_criteria="Farmers, tenant farmers, sharecroppers, and self-help groups engaged in agriculture may apply through banks.",
            application_url="https://www.myscheme.gov.in/",
            is_eligible=None,
        ),
    ]

    if any(term in q for term in ("insurance", "bima", "crop insurance", "fasal")):
        return [catalogue[0], catalogue[1], catalogue[2]]
    if any(term in q for term in ("loan", "credit", "kcc")):
        return [catalogue[2], catalogue[1]]
    return catalogue


def _build_advisory(query: str, state: str, crop: str, schemes: list[SchemeResult]) -> str:
    context = []
    if query:
        context.append(f"query '{query}'")
    if crop:
        context.append(f"crop '{crop}'")
    if state:
        context.append(f"state '{state}'")
    suffix = " for " + ", ".join(context) if context else ""
    return (
        f"Found {len(schemes)} relevant government scheme option(s){suffix}. "
        "Open each result to review benefits, eligibility, and the official application link."
    )
