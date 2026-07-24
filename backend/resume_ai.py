from pdfminer.high_level import extract_text
import os


# -------------------------
# Skill Categories
# -------------------------

CORE_SKILLS = [
    "python", "java", "c++", "sql",
    "fastapi", "django", "flask",
    "mongodb", "mysql", "postgresql"
]

ML_SKILLS = [
    "machine learning", "deep learning",
    "data science", "pandas", "numpy",
    "tensorflow", "pytorch", "scikit"
]

DEVOPS_SKILLS = [
    "docker", "kubernetes", "aws",
    "azure", "ci/cd", "git"
]

STRUCTURE_SECTIONS = [
    "experience", "projects",
    "education", "skills"
]


# -------------------------
# Resume Analyzer
# -------------------------

def analyze_resume(file_path: str) -> int:
    """
    Analyze resume PDF and return score (0-100)
    """

    if not os.path.exists(file_path):
        return 0

    try:
        text = extract_text(file_path)

        if not text or len(text.strip()) < 50:
            return 40

        text_lower = text.lower()
        score = 0

        # -------------------------
        # Skill Scoring
        # -------------------------

        for skill in CORE_SKILLS:
            if skill in text_lower:
                score += 6

        for skill in ML_SKILLS:
            if skill in text_lower:
                score += 4

        for skill in DEVOPS_SKILLS:
            if skill in text_lower:
                score += 4

        # -------------------------
        # Structure Scoring
        # -------------------------

        for section in STRUCTURE_SECTIONS:
            if section in text_lower:
                score += 5

        # -------------------------
        # Length Quality
        # -------------------------

        length_bonus = min(len(text) // 300, 15)
        score += length_bonus

        # -------------------------
        # Experience Bonus
        # -------------------------

        if "intern" in text_lower:
            score += 5

        if "github" in text_lower:
            score += 5

        if "project" in text_lower:
            score += 5

        return min(score, 100)

    except Exception:
        return 30  # fallback score
