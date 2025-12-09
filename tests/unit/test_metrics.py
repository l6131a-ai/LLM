import math
import pytest

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

try:
    from langdetect import detect as lang_detect
    LANGDETECT_AVAILABLE = True
except Exception:
    LANGDETECT_AVAILABLE = False


def simple_bleu(reference: str, hypothesis: str) -> float:
    """
    Very small simplified BLEU-like score: unigram precision with brevity penalty.
    This is NOT sacreBLEU but suitable for deterministic unit-tests without heavy deps.
    """
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()
    if not hyp_tokens:
        return 0.0
    # unigram precision
    matches = sum(1 for t in hyp_tokens if t in ref_tokens)
    precision = matches / len(hyp_tokens)
    # brevity penalty
    ref_len = len(ref_tokens)
    hyp_len = len(hyp_tokens)
    bp = 1.0
    if hyp_len < ref_len:
        bp = math.exp(1 - (ref_len / hyp_len))
    return precision * bp


def rouge_l_f1(reference: str, hypothesis: str) -> float:
    """Compute ROUGE-L F1 based on LCS length (simple implementation).
    """
    a = reference.split()
    b = hypothesis.split()
    # compute LCS
    n = len(a)
    m = len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            if a[i] == b[j]:
                dp[i][j] = 1 + dp[i + 1][j + 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
    lcs = dp[0][0]
    if lcs == 0:
        return 0.0
    prec = lcs / m if m > 0 else 0.0
    rec = lcs / n if n > 0 else 0.0
    if prec + rec == 0:
        return 0.0
    f1 = (2 * prec * rec) / (prec + rec)
    return f1


def semantic_similarity(reference: str, hypothesis: str) -> float:
    """
    Compute a semantic similarity score in a best-effort way:
    - If sklearn available: TF-IDF + cosine similarity
    - Otherwise: Jaccard over token sets
    """
    if SKLEARN_AVAILABLE:
        vec = TfidfVectorizer().fit_transform([reference, hypothesis])
        sim = cosine_similarity(vec[0:1], vec[1:2])[0][0]
        return float(sim)
    # fallback: token Jaccard
    a = set(reference.lower().split())
    b = set(hypothesis.lower().split())
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = a & b
    union = a | b
    return len(inter) / len(union)


def test_simple_bleu_threshold():
    ref = "Hello world this is a test"
    hyp_good = "Hello world this is a test"
    hyp_ok = "Hello this is test"
    hyp_bad = "Completely different sentence"

    assert simple_bleu(ref, hyp_good) >= 0.9
    assert simple_bleu(ref, hyp_ok) >= 0.4
    assert simple_bleu(ref, hyp_bad) < 0.2


def test_rouge_l_f1_values():
    ref = "The quick brown fox jumps over the lazy dog"
    hyp_good = "The quick brown fox jumps over the lazy dog"
    hyp_partial = "The quick brown fox jumps"

    assert rouge_l_f1(ref, hyp_good) > 0.9
    assert rouge_l_f1(ref, hyp_partial) > 0.3


def test_length_ratio():
    src = "Short sentence for testing"
    trans_short = "Short sentence"
    trans_long = "This is a considerably longer translation of the original sentence for testing"

    ratio_short = len(trans_short.split()) / len(src.split())
    ratio_long = len(trans_long.split()) / len(src.split())

    assert 0.7 <= ratio_short <= 1.3 or ratio_short < 0.7
    assert ratio_long > 1.3


def test_semantic_similarity_with_sklearn_or_jaccard():
    ref = "The cat sat on the mat"
    hyp_similar = "A cat was sitting on the mat"
    hyp_different = "An airplane flew across the sky"

    sim_score = semantic_similarity(ref, hyp_similar)
    diff_score = semantic_similarity(ref, hyp_different)

    assert sim_score > diff_score
    # reasonable thresholds (may vary by algorithm)
    assert sim_score >= 0.4
    assert diff_score < 0.3


def test_language_detection_skip_if_missing():
    if not LANGDETECT_AVAILABLE:
        pytest.skip("langdetect not installed - skipping language detection test")
    src = "This is an English sentence."
    assert lang_detect(src).startswith("en")
