import os
from typing import Union, Any
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.index import create_in, open_dir, FileIndex
from whoosh.qparser import QueryParser
from whoosh.searching import Results
from pkb.utils.logging import getLogging
logging = getLogging()

md_schema = Schema(path=ID(stored=True), tags=KEYWORD, title=TEXT(stored=True), content=TEXT)

# environment variables
collection = os.getenv('SEARCH_DB_DIR', 'collection') 
logging.info(f"####### SEARCH_DB_DIR: {collection} #######")

def create_collection() -> Union[FileIndex, bool]:
    if not os.path.exists(collection):
        logging.info(f"####### search collection folder created under path '{collection}' #######")
        os.mkdir(collection)
        return create_in(collection, md_schema), True
    else:
        logging.info(f"####### search collection folder detected under path '{collection}' #######")
        return open_dir(collection), False
        
def get_indexer() -> FileIndex:
    return open_dir(collection)

def search_doc(field, query) -> (Results | Any):
    ix = get_indexer()
    with ix.searcher() as searcher:
        query = QueryParser(field, ix.schema).parse(query)
        return searcher.search_doc(query)

def create_dummy_data() -> bool:
    ix, created = create_collection()
    if not created: 
        writer = ix.writer()
        writer.add_document(title="My document", content="This is my document!", path="/a", tags="x y")
        writer.add_document(title="Second try", content="This is the second example.", path="/b", tags="y z")
        writer.add_document(title="Third time's the charm", content="Examples are many.", path="/c", tags="x y z")
        writer.commit()
        logging.info(f"####### search collection folder create under path '{collection}' and dummy data populated #######")
        return True
    else: 
        logging.info(f"####### search collection folder detected under path '{collection}' #######")
        return False







