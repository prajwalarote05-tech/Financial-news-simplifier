import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    print("=" * 60)
    print("FINNEWS AI — Comprehensive Automated Test Suite")
    print("=" * 60)

    client = httpx.Client(base_url=BASE_URL, timeout=15.0)

    # 1. Health check
    print("\n[1] Testing GET /api/health...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    health_data = res.json()
    assert health_data["status"] == "healthy"
    assert health_data["service"] == "FINNEWS AI"
    print(f"    PASSED: status={health_data['status']}, version={health_data['version']}")

    # 2. News endpoint
    print("\n[2] Testing GET /api/news...")
    res = client.get("/api/news")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    news_data = res.json()
    assert news_data["success"] is True
    assert len(news_data["articles"]) > 0
    print(f"    PASSED: total_results={news_data['total_results']}, fetched={len(news_data['articles'])} articles")

    # 3. News with category filter
    print("\n[3] Testing GET /api/news?category=Economy...")
    res = client.get("/api/news?category=Economy")
    assert res.status_code == 200
    econ_data = res.json()
    assert econ_data["success"] is True
    for art in econ_data["articles"]:
        assert art["category"] == "Economy"
    print(f"    PASSED: {len(econ_data['articles'])} Economy articles returned.")

    # 4. News with search query
    print("\n[4] Testing GET /api/news?search=Nvidia...")
    res = client.get("/api/news?search=Nvidia")
    assert res.status_code == 200
    search_data = res.json()
    assert search_data["success"] is True
    print(f"    PASSED: {len(search_data['articles'])} articles matching 'Nvidia'")

    # 5. Summarize endpoint
    print("\n[5] Testing POST /api/summarize...")
    payload = {
        "title": "Federal Reserve Cuts Rates by 50 Basis Points",
        "content": "The central bank lowered benchmark borrowing costs to boost economic growth.",
        "description": "Fed moves forward with aggressive monetary policy easing."
    }
    res = client.post("/api/summarize", json=payload)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    sum_data = res.json()
    assert sum_data["success"] is True
    assert len(sum_data["summary"]) > 0
    assert len(sum_data["key_points"]) > 0
    assert len(sum_data["why_it_matters"]) > 0
    assert len(sum_data["terms"]) > 0
    print(f"    PASSED: Summary generated, {len(sum_data['key_points'])} key points, {len(sum_data['terms'])} glossary terms.")

    # 6. Combined endpoint
    print("\n[6] Testing GET /api/financial-news...")
    res = client.get("/api/financial-news?limit=4")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    comb_data = res.json()
    assert comb_data["success"] is True
    assert comb_data["total_fetched"] > 0
    assert comb_data["total_simplified"] > 0
    assert comb_data["sources_count"] > 0
    assert len(comb_data["articles"]) == 4
    first_art = comb_data["articles"][0]
    assert first_art["simplified"] is True
    assert first_art["summary"] is not None
    print(f"    PASSED: Combined payload ready with {comb_data['total_simplified']} simplified articles.")

    # 7. Frontend static pages
    print("\n[7] Testing GET / (Frontend Dashboard)...")
    res = client.get("/")
    assert res.status_code == 200
    assert "FINNEWS" in res.text
    print("    PASSED: Dashboard index.html successfully served.")

    print("\n[8] Testing GET /about (Frontend About Page)...")
    res = client.get("/about")
    assert res.status_code == 200
    assert "About" in res.text
    print("    PASSED: About page successfully served.")

    print("\n" + "=" * 60)
    print("ALL 8 AUTOMATED TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_endpoints()
    except Exception as e:
        print(f"\nTEST FAILED: {e}", file=sys.stderr)
        sys.exit(1)
