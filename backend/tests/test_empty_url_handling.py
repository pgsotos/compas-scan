"""
Test for empty URL handling in compas_core.

This test verifies that candidates with empty or missing link fields
are properly filtered out and don't cause Pydantic validation errors.
"""

from api.compas_core import _classify_all_candidates
from api.mocks import clean_url
from api.models import BrandContext, CompetitorCandidate


def test_clean_url_returns_empty_string_for_invalid_input():
    """Verify clean_url behavior with empty/None inputs."""
    assert clean_url("") == ""
    assert clean_url(None) == ""
    assert clean_url("https://valid.com") == "https://valid.com"


def test_empty_url_candidate_is_discarded():
    """
    Test that candidates with empty clean_url are properly discarded
    and don't cause validation errors when creating Competitor objects.
    """
    # Create a candidate with empty clean_url (simulating the bug scenario)
    candidates = [
        CompetitorCandidate(link="", clean_url="", title="Some Title", snippet="Some snippet", source="search"),
        CompetitorCandidate(
            link="https://valid-competitor.com",
            clean_url="https://valid-competitor.com",
            title="Valid Competitor",
            snippet="A real competitor",
            source="search",
        ),
    ]

    context = BrandContext(
        name="TestBrand", url="https://testbrand.com", country="US", tld="com", keywords=["test", "brand"]
    )

    # This should not raise a validation error
    hda, lda, discarded = _classify_all_candidates(candidates, context)

    # The empty URL candidate should be in discarded
    assert len(discarded) >= 1

    # Find the discarded candidate with empty URL
    empty_url_discarded = [d for d in discarded if d.url == "(empty URL)"]
    assert len(empty_url_discarded) == 1
    assert "Empty or invalid URL" in empty_url_discarded[0].reason

    # Valid candidates should be processed normally (might be HDA, LDA, or discarded)
    total_processed = len(hda) + len(lda) + len([d for d in discarded if d.url != "(empty URL)"])
    assert total_processed == 1


def test_invalid_netloc_is_handled():
    """
    Test that URLs with empty netloc are properly handled
    (e.g., malformed URLs that pass clean_url but have no domain).
    """
    candidates = [
        CompetitorCandidate(link="http://", clean_url="http://", title="Malformed URL", snippet="Test", source="search")
    ]

    context = BrandContext(name="TestBrand", url="https://testbrand.com", country="US", tld="com", keywords=["test"])

    # Should not raise validation error
    hda, lda, discarded = _classify_all_candidates(candidates, context)

    # Should be discarded
    assert len(discarded) >= 1
    print(f"Discarded: {[(d.url, d.reason) for d in discarded]}")
    # Check that it was either caught by our validation or by classify_competitor
    assert any(
        "Invalid URL structure" in d.reason
        or "empty domain" in d.reason
        or "Empty or invalid URL" in d.reason
        or d.url == "http://"  # At minimum, it should be discarded
        for d in discarded
    )


if __name__ == "__main__":
    print("Running empty URL handling tests...\n")

    test_clean_url_returns_empty_string_for_invalid_input()
    print("✅ test_clean_url_returns_empty_string_for_invalid_input passed")

    test_empty_url_candidate_is_discarded()
    print("✅ test_empty_url_candidate_is_discarded passed")

    test_invalid_netloc_is_handled()
    print("✅ test_invalid_netloc_is_handled passed")

    print("\n🎉 All tests passed!")
