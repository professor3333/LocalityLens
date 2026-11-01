"""Whatever the input, the rules baseline must emit output that passes validation."""

from hypothesis import given
from hypothesis import strategies as st

from localitylens.baseline.rules import Lexicon, RulesExtractor
from localitylens.extract.validate import Severity, validate_extraction
from localitylens.ingest.normalize import normalize

RULES = RulesExtractor(
    Lexicon.from_names(
        ["Larimer", "Boulder", "El Paso"], ["Longs Peak", "Lyons", "Boulder", "Bear Lake"]
    )
)

FRAGMENTS = [
    "2 mi", "NE", "of", "Longs Peak", "summit", "Larimer Co.", "Colo.", "3 m", "E", "N.E.",
    "½", "1 1/2", "0", "km", "ft.", "from", "near", "nr.", "about", "ca.", "?", "along the trail",
    "by road", "between", "and", "Lyons", "Boulder", "Hwy 34", "R73W", "T5N", "Mt.", "Pk.",
    "Bear lake", "Elev", "Sept.", ",", ".", ";", "s. loc.", "up", "Canyon", "Gold Hill Mine",
]  # fmt: skip

texts = st.one_of(
    st.lists(st.sampled_from(FRAGMENTS), max_size=14).map(" ".join),
    st.text(max_size=120),
    st.lists(
        st.one_of(
            st.sampled_from(FRAGMENTS), st.text(alphabet="AbcNESW .,0123456789/", max_size=8)
        ),
        max_size=12,
    ).map(" ".join),
)


@given(texts)
def test_rules_output_always_validates(original: str) -> None:
    n = normalize(original)
    out = RULES.extract(n.text)
    result = validate_extraction(out, n)
    assert [i for i in result.issues if i.severity is Severity.ERROR] == []
