import pytest
import json
import os
from time import sleep

from rara_tools.elastic import KataElastic

with open("./tests/test_data/elastic_docs.json") as fh:
    TEST_DOCUMENTS = json.load(fh)

es_url = os.getenv("ELASTIC_TEST_URL", "http://localhost:9200")
ELASTIC = KataElastic(es_url)
ELASTIC_BAD = KataElastic("http://locallost:9012")
TEST_INDEX_NAME = "tools_testing_index"
TEST_DOCUMENT_ID = None


@pytest.mark.order(1)
def test_index_creation_and_data_indexing():
    """ Tests if index created and documents indexed.
    """
    # Create test index
    created = ELASTIC.create_index(TEST_INDEX_NAME)
    assert created["acknowledged"] is True
    # Add test documents
    for document in TEST_DOCUMENTS:
        indexed = ELASTIC.index_document(TEST_INDEX_NAME, document)
        assert indexed["result"] == "created"
    # let it index
    sleep(1)

@pytest.mark.order(2)
def test_check():
    """Tests health check method.
    """
    assert ELASTIC.check() is True
    # test bad connection
    assert ELASTIC_BAD.check() is False

@pytest.mark.order(3)
def test_get_document_by_key():
    """Tests if correct documents fetched.
    """
    result = ELASTIC.get_documents_by_key(TEST_INDEX_NAME, "foo")
    assert len(result) == 2
    result = ELASTIC.get_documents_by_key(TEST_INDEX_NAME, "bar")
    global TEST_DOCUMENT_ID
    TEST_DOCUMENT_ID = result[0].meta.id
    assert len(result) == 1
    result = ELASTIC.get_documents_by_key(TEST_INDEX_NAME, "loll")
    assert len(result) == 0

@pytest.mark.order(5)
def test_document_deleting():
    """ Tests deleting a document from index.
    """
    deleted = ELASTIC.delete_document(TEST_INDEX_NAME, TEST_DOCUMENT_ID)
    assert deleted["result"] == "deleted"
    sleep(1)
    # check if document was actually deleted
    result = ELASTIC.get_documents_by_key(TEST_INDEX_NAME, "bar")
    assert len(result) == 0

@pytest.mark.order(5)
def test_index_deleting():
    """ Tests deleting index. We delete the test index now.
    """
    deleted = ELASTIC.delete_index(TEST_INDEX_NAME)
    assert deleted["acknowledged"] is True
