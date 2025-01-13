from typing import Iterator, List

from ethosian.document import Document
from ethosian.document.reader.arxiv import ArxivReader
from ethosian.knowledge.agent import AgentKnowledge


class ArxivKnowledgeBase(AgentKnowledge):
    queries: List[str] = []
    reader: ArxivReader = ArxivReader()

    @property
    def document_lists(self) -> Iterator[List[Document]]:
        """Iterate over urls and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
            Iterator[List[Document]]: Iterator yielding list of documents
        """

        for _query in self.queries:
            yield self.reader.read(query=_query)
