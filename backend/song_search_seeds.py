
"""Search terms for expanding our Hindi song catalog.

Categories are discovery hints, not verified song classifications.
Gemini enrichment and later validation handle classification.
"""

SONG_SEARCH_SEEDS = [
    {
        "title": "Raghupati Raghav Raja Ram",
        "category_hint": "devotional",
    },
    {
        "title": "Achyutam Keshavam",
        "category_hint": "devotional",
    },
    {
        "title": "Yashomati Maiya Se Bole Nandlala",
        "category_hint": "krishna_bhajan",
    },
    {
        "title": "Shri Krishna Govind Hare Murari",
        "category_hint": "krishna_bhajan",
    },
    {
        "title": "Nimbuda Nimbuda",
        "category_hint": "folk",
    },
    {
        "title": "Kesariya Balam",
        "category_hint": "folk",
    },
    {
        "title": "Dholida Dhol Re Vagad",
        "category_hint": "garba",
    },
    {
        "title": "Tara Vina Shyam",
        "category_hint": "garba",
    },
    {
        "title": "Ae Mere Watan Ke Logon",
        "category_hint": "patriotic",
    },
    {
        "title": "Vande Mataram",
        "category_hint": "patriotic",
    },
]


def get_search_seeds():
    """Return independent copies of the configured search seeds."""
    return [dict(seed) for seed in SONG_SEARCH_SEEDS]


def get_category_counts():
    """Count discovery search terms by category."""
    counts = {}

    for seed in SONG_SEARCH_SEEDS:
        category = seed["category_hint"]
        counts[category] = counts.get(category, 0) + 1

    return counts


if __name__ == "__main__":
    print("========== SONG SEARCH SEEDS ==========")

    for seed in get_search_seeds():
        print(f"{seed['category_hint']}: {seed['title']}")

    print("\nCategory counts:", get_category_counts())

