import re


# -------------------------
# Skill Categories
# -------------------------

CORE_KEYWORDS = [
    "python", "java", "c++", "backend",
    "api", "rest", "database",
    "sql", "mongodb", "django",
    "fastapi", "flask"
]

ADVANCED_TERMS = [
    "authentication", "authorization",
    "scalability", "optimization",
    "deployment", "docker",
    "microservices", "async",
    "jwt", "caching"
]

EXPERIENCE_TERMS = [
    "project", "intern", "experience",
    "implemented", "developed",
    "built", "designed"
]


# -------------------------
# Interview Evaluator
# -------------------------

def evaluate_interview(answer: str) -> int:
    """
    Intelligent heuristic-based interview scoring (0–100)
    """

    if not answer or len(answer.strip()) < 20:
        return 30

    answer = answer.strip()
    answer_lower = answer.lower()
    score = 0

    word_count = len(answer.split())

    # -------------------------
    # Length Quality
    # -------------------------

    if word_count > 40:
        score += 20
    elif word_count > 25:
        score += 12
    else:
        score += 5

    # -------------------------
    # Keyword Diversity
    # -------------------------

    unique_hits = 0
    for keyword in CORE_KEYWORDS:
        if keyword in answer_lower:
            unique_hits += 1

    score += min(unique_hits * 6, 30)

    # -------------------------
    # Advanced Knowledge
    # -------------------------

    advanced_hits = 0
    for term in ADVANCED_TERMS:
        if term in answer_lower:
            advanced_hits += 1

    score += min(advanced_hits * 5, 20)

    # -------------------------
    # Real Experience Mention
    # -------------------------

    experience_hits = 0
    for term in EXPERIENCE_TERMS:
        if term in answer_lower:
            experience_hits += 1

    score += min(experience_hits * 4, 15)

    # -------------------------
    # Sentence Structure Check
    # -------------------------

    sentences = re.split(r"[.!?]", answer)
    valid_sentences = [s for s in sentences if len(s.split()) > 5]

    if len(valid_sentences) >= 3:
        score += 10

    # -------------------------
    # Anti-Keyword Stuffing
    # -------------------------

    if word_count > 0:
        keyword_density = unique_hits / word_count
        if keyword_density > 0.2:
            score -= 10

    return max(30, min(score, 100))
