from note_crawler.models import Article, Creator


def test_creator_from_api_with_data_envelope():
    payload = {
        "data": {
            "id": 1,
            "urlname": "foo",
            "nickname": "Foo",
            "profile": "p",
            "noteCount": 3,
            "followerCount": 10,
            "followingCount": 2,
            "profileImageUrl": "https://x/y.jpg",
        }
    }
    c = Creator.from_api(payload)
    assert c.id == 1
    assert c.urlname == "foo"
    assert c.note_count == 3


def test_article_from_list_item_and_url():
    item = {
        "key": "nabc123",
        "slug": "nabc123",
        "name": "hello / world",
        "type": "TextNote",
        "status": "published",
        "publishAt": "2025-10-24T11:46:58+09:00",
        "likeCount": 5,
        "price": 0,
        "description": "d",
        "eyecatch": "https://x/e.jpg",
    }
    a = Article.from_list_item(item, creator_urlname="foo")
    assert a.url == "https://note.com/foo/n/nabc123"
    assert a.is_paid is False
    assert a.filename_stem.startswith("2025-10-24_")
    assert "/" not in a.filename_stem


def test_article_attach_detail_sets_body():
    a = Article.from_list_item({"key": "k", "name": "t", "price": 0}, "foo")
    a.attach_detail({"data": {"body": "<p>hi</p>", "comment_count": 2}})
    assert a.body_html == "<p>hi</p>"
    assert a.comment_count == 2
