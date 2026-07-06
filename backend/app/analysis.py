from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import Any

from app.models import Certification, HalalRule, HealthRule, Ingredient

HALAL_LABELS = {
    "CERTIFIED_HALAL": "Certified Halal",
    "NO_PROHIBITED_INGREDIENT_FOUND": "No prohibited ingredient found",
    "HARAM": "Haram",
    "DOUBTFUL": "Doubtful / Mushbooh",
    "UNKNOWN": "Unknown / Needs verification",
}


@dataclass
class Match:
    original: str
    status: str
    health_status: str
    reason: str
    matched: bool
    matched_name: str | None = None
    risk_level: int = 0


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().replace("&", " and ")
    value = re.sub(r"\be[\s\-]*(\d{3,4}[a-z]?)\b", r"e\1", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def split_ingredients(text: str) -> list[str]:
    text = re.sub(r"(?i)^\s*ingredients?\s*[:\-]", "", text.strip())
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in text:
        if char in "([{" :
            depth += 1
        elif char in ")]}":
            depth = max(0, depth - 1)
        if char in ",;\n" and depth == 0:
            value = "".join(current).strip(" .:-")
            if value:
                parts.append(value)
            current = []
        else:
            current.append(char)
    value = "".join(current).strip(" .:-")
    if value:
        parts.append(value)

    cleaned: list[str] = []
    for part in parts:
        part = re.sub(r"\s+", " ", part).strip()
        if len(part) >= 2 and part.lower() not in {"ingredients", "contains"}:
            cleaned.append(part)
    return cleaned[:250]


def _ingredient_terms(ingredient: Ingredient) -> list[str]:
    terms = [ingredient.name, *(ingredient.aliases or [])]
    if ingredient.e_number:
        terms.append(ingredient.e_number)
    return sorted({normalize(term) for term in terms if term}, key=len, reverse=True)


def match_ingredient(
    original: str,
    ingredients: Iterable[Ingredient],
    rules: Iterable[HalalRule],
) -> Match:
    normalized = normalize(original)
    best: tuple[int, Ingredient] | None = None
    for ingredient in ingredients:
        for term in _ingredient_terms(ingredient):
            if not term:
                continue
            exact_or_phrase = normalized == term or re.search(rf"\b{re.escape(term)}\b", normalized)
            if exact_or_phrase and (best is None or len(term) > best[0]):
                best = (len(term), ingredient)

    if best:
        ingredient = best[1]
        return Match(
            original=original,
            status=ingredient.halal_status,
            health_status=ingredient.health_status,
            reason=ingredient.explanation,
            matched=True,
            matched_name=ingredient.name,
            risk_level=ingredient.risk_level,
        )

    for rule in rules:
        keyword = normalize(rule.keyword)
        if keyword and re.search(rf"\b{re.escape(keyword)}\b", normalized):
            return Match(
                original=original,
                status=rule.status,
                health_status="NEUTRAL",
                reason=rule.reason,
                matched=True,
                matched_name=rule.keyword,
                risk_level=4 if rule.status == "HARAM" else 2,
            )

    return Match(
        original=original,
        status="UNKNOWN",
        health_status="UNKNOWN",
        reason="This ingredient is not yet in the verified database.",
        matched=False,
    )


def active_certificate(certifications: Iterable[Certification]) -> Certification | None:
    today = date.today()
    for certificate in certifications:
        if certificate.status != "ACTIVE":
            continue
        if certificate.valid_from and certificate.valid_from > today:
            continue
        if certificate.valid_until and certificate.valid_until < today:
            continue
        return certificate
    return None


def calculate_halal(matches: list[Match], certificate: Certification | None) -> dict[str, Any]:
    haram = [m for m in matches if m.status == "HARAM"]
    doubtful = [m for m in matches if m.status == "DOUBTFUL"]
    unknown = [m for m in matches if m.status == "UNKNOWN"]
    known = [m for m in matches if m.status != "UNKNOWN"]

    reasons: list[str] = []
    if haram:
        status = "HARAM"
        reasons.append("A confirmed prohibited ingredient was detected.")
    elif certificate:
        status = "CERTIFIED_HALAL"
        reasons.append(f"An active certificate from {certificate.authority_name} was found.")
    elif doubtful:
        status = "DOUBTFUL"
        reasons.append("One or more ingredients require their source or processing method to be verified.")
    elif unknown:
        status = "UNKNOWN"
        reasons.append("Some ingredients could not be matched with verified data.")
    elif matches and len(known) == len(matches):
        status = "NO_PROHIBITED_INGREDIENT_FOUND"
        reasons.append("No prohibited ingredient was found in the supplied list.")
    else:
        status = "UNKNOWN"
        reasons.append("There is not enough information to make an ingredient-based assessment.")

    coverage = (len(known) / len(matches)) if matches else 0
    if status == "HARAM":
        confidence = min(99, 88 + len(haram) * 4)
    elif status == "CERTIFIED_HALAL":
        confidence = 95
    elif status == "DOUBTFUL":
        confidence = min(95, int(65 + coverage * 25))
    elif status == "NO_PROHIBITED_INGREDIENT_FOUND":
        confidence = min(90, int(60 + coverage * 30))
    else:
        confidence = max(20, int(coverage * 60))

    risky = [
        {
            "name": match.original,
            "status": match.status,
            "reason": match.reason,
            "matched_name": match.matched_name,
        }
        for match in matches
        if match.status in {"HARAM", "DOUBTFUL", "UNKNOWN"}
    ]
    for match in [*haram, *doubtful, *unknown][:4]:
        reasons.append(f"{match.original}: {match.reason}")

    certificate_payload = {
        "found": certificate is not None,
        "status": certificate.status if certificate else "UNVERIFIED",
        "authority": certificate.authority_name if certificate else None,
        "certificate_number": certificate.certificate_number if certificate else None,
        "valid_until": certificate.valid_until.isoformat() if certificate and certificate.valid_until else None,
        "verification_url": certificate.verification_url if certificate else None,
    }

    return {
        "status": status,
        "label": HALAL_LABELS[status],
        "confidence": confidence,
        "reasons": reasons[:8],
        "risky_ingredients": risky[:20],
        "certificate": certificate_payload,
    }


def number(nutrition: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = nutrition.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def calculate_health(
    matches: list[Match],
    nutrition: dict[str, Any] | None,
    health_rules: Iterable[HealthRule] = (),
) -> dict[str, Any]:
    nutrition = nutrition or {}
    reasons: list[str] = []
    numeric_fields = 0

    sugar = number(nutrition, "sugars_100g", "sugar", "sugars")
    saturated = number(nutrition, "saturated_fat_100g", "saturated_fat")
    sodium = number(nutrition, "sodium_100g", "sodium")
    salt = number(nutrition, "salt_100g", "salt")
    trans_fat = number(nutrition, "trans_fat_100g", "trans_fat")
    fiber = number(nutrition, "fiber_100g", "fiber")
    protein = number(nutrition, "proteins_100g", "protein")

    if sodium is not None and sodium < 20:  # Open Food Facts usually stores grams.
        sodium *= 1000

    checks = [sugar, saturated, sodium, salt, trans_fat, fiber, protein]
    numeric_fields = sum(value is not None for value in checks)
    score = 100 if numeric_fields else 70
    major_warnings = 0

    if sugar is not None:
        if sugar > 22.5:
            score -= 25
            major_warnings += 1
            reasons.append("High sugar per 100 g.")
        elif sugar > 10:
            score -= 12
            reasons.append("Moderate-to-high sugar.")
    if saturated is not None:
        if saturated > 5:
            score -= 20
            major_warnings += 1
            reasons.append("High saturated fat.")
        elif saturated > 2:
            score -= 8
            reasons.append("Moderate saturated fat.")
    if sodium is not None:
        if sodium > 600:
            score -= 20
            major_warnings += 1
            reasons.append("High sodium.")
        elif sodium > 300:
            score -= 10
            reasons.append("Moderate sodium.")
    elif salt is not None:
        if salt > 1.5:
            score -= 20
            major_warnings += 1
            reasons.append("High salt.")
        elif salt > 0.75:
            score -= 10
            reasons.append("Moderate salt.")
    if trans_fat is not None and trans_fat > 0.5:
        score -= 25
        major_warnings += 1
        reasons.append("Contains notable trans fat.")
    if fiber is not None and fiber >= 6:
        score += 10
        reasons.append("Good source of fibre.")
    elif fiber is not None and fiber < 2:
        score -= 8
        reasons.append("Low fibre.")
    if protein is not None and protein >= 10:
        score += 8
        reasons.append("Provides useful protein.")

    if major_warnings >= 2:
        score -= 10
        reasons.append("Multiple nutrients are high.")

    # Ingredient-based fallback and adjustment.
    for match in matches:
        if match.health_status == "UNHEALTHY":
            score -= max(4, match.risk_level * 3)
            if len(reasons) < 8:
                reasons.append(f"{match.original} should be limited in frequent consumption.")
        elif match.health_status == "HEALTHY":
            score += 3

    # Optional editable database rules override/add to the built-in MVP thresholds.
    for rule in health_rules:
        value = number(nutrition, rule.nutrient)
        if value is None:
            continue
        triggered = False
        if rule.maximum_value is not None and value > rule.maximum_value:
            triggered = True
        if rule.minimum_value is not None and value < rule.minimum_value:
            triggered = True
        if triggered:
            score += rule.score_change
            reasons.append(rule.message)

    score = max(0, min(100, score))
    if numeric_fields == 0 and not matches:
        return {
            "status": "UNKNOWN",
            "score": 0,
            "confidence": 10,
            "reasons": ["No nutrition or ingredient information was available."],
        }

    if score >= 80:
        status = "HEALTHY"
    elif score >= 50:
        status = "MODERATE"
    else:
        status = "UNHEALTHY"

    confidence = min(95, 45 + numeric_fields * 7) if numeric_fields else 55
    if not reasons:
        reasons.append("No major nutrition warning was detected from the available data.")
    return {
        "status": status,
        "score": score,
        "confidence": confidence,
        "reasons": list(dict.fromkeys(reasons))[:8],
    }


def recommendation(halal: dict[str, Any], health: dict[str, Any]) -> str:
    if halal["status"] == "HARAM":
        return "Avoid this product and choose a verified halal alternative."
    if halal["status"] in {"DOUBTFUL", "UNKNOWN"}:
        return "Check the ingredient source or an official halal certificate before consuming it."
    if health["status"] == "UNHEALTHY":
        return "This may be permissible, but choose a lower-sugar, lower-salt or higher-fibre option more often."
    if health["status"] == "MODERATE":
        return "Suitable in moderation; check the serving size and balance it with less processed foods."
    return "The available data shows no major concern. Keep portion size and overall diet in mind."
