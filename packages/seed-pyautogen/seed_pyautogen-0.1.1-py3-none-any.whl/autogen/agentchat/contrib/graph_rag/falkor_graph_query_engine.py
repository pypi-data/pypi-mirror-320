import os
import warnings
from typing import List
import requests

from falkordb import FalkorDB, Graph
from graphrag_sdk import KnowledgeGraph, Source
from graphrag_sdk.model_config import KnowledgeGraphModelConfig
from graphrag_sdk.models import GenerativeModel
from graphrag_sdk.models.azure_openai import AzureOpenAiGenerativeModel
from graphrag_sdk.models.openai import OpenAiGenerativeModel
from graphrag_sdk.ontology import Ontology
from autogen.agentchat.contrib.graph_rag.document import Document, DocumentType

from .document import Document
from .graph_query_engine import GraphStoreQueryResult


class FalkorGraphQueryEngine:
    """
    This is a wrapper for FalkorDB KnowledgeGraph.
    """

    def __init__(
        self,
        name: str,
        host: str = "127.0.0.1",
        port: int = 6379,
        username: str | None = None,
        password: str | None = None,
        model_name: str = "gpt-4o",
        model_type: str = "azure",
        ontology: Ontology | None = None,
    ):
        """
        Initialize a FalkorDB knowledge graph.
        Please also refer to https://github.com/FalkorDB/GraphRAG-SDK/blob/main/graphrag_sdk/kg.py

        Args:
            name (str): Knowledge graph name.
            host (str): FalkorDB hostname.
            port (int): FalkorDB port number.
            username (str|None): FalkorDB username.
            password (str|None): FalkorDB password.
            model_name (str): Name of the generative model to use, default is "gpt-4o".
            model_type (str): Model type to use for generative model, default is "azure".
                            Options are "azure" (AzureOpenAiGenerativeModel) or "openai" (OpenAiGenerativeModel).
            ontology: FalkorDB knowledge graph schema/ontology, https://github.com/FalkorDB/GraphRAG-SDK/blob/main/graphrag_sdk/ontology.py
                If None, FalkorDB will auto generate an ontology from the input docs.
        """
        # Configure the generative model based on api_type
        if model_type.lower() == "azure":
            self.model: GenerativeModel = AzureOpenAiGenerativeModel(model_name)
        elif model_type.lower() == "openai":
            self.model: GenerativeModel = OpenAiGenerativeModel(model_name)
        else:
            raise ValueError(f"Invalid api_type '{model_type}'. Expected 'azure' or 'openai'.")
        
        self.name = name
        self.ontology_table_name = name + "_ontology"
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.model: GenerativeModel = AzureOpenAiGenerativeModel(model_name)
        self.model_config = KnowledgeGraphModelConfig.with_model(self.model)
        self.ontology = ontology
        self.knowledge_graph = None
        self.falkordb = FalkorDB(host=self.host, port=self.port, username=self.username, password=self.password)

    def connect_db(self):
        """
        Connect to an existing knowledge graph. If the graph does not exist, build the knowledge graph with fixed url.
        """
        if self.name in self.falkordb.list_graphs():
            try:
                self.ontology = self._load_ontology_from_db(self.name)
            except Exception:
                warnings.warn("Graph Ontology is not loaded.")

            if self.ontology is None:
                raise ValueError(f"Ontology of the knowledge graph '{self.name}' can't be None.")

            self.knowledge_graph = KnowledgeGraph(
                name=self.name,
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                model_config=self.model_config,
                ontology=self.ontology,
            )

            # Establishing a chat session will maintain the history
            self._chat_session = self.knowledge_graph.chat_session()
        else:
            # Build the knowledge graph with Seed_Knowledge_Graph.txt if it does not exist
            test_doc_path = "https://seed-resource.oss-cn-beijing.aliyuncs.com/Seed_Knowledge_Graph.txt"
            text_doc = [Document(doctype=DocumentType.URL, path_or_url=test_doc_path)]
            self.init_db(input_doc=text_doc)

    def init_db(self, input_doc: List[Document]):
        """
        Build the knowledge graph with input documents.
        """
        sources = []
        for doc in input_doc:
            if os.path.exists(doc.path_or_url):
                # Local file
                sources.append(Source(doc.path_or_url))
            elif doc.path_or_url.startswith("http://") or doc.path_or_url.startswith("https://"):
                # Remote URL
                try:
                    response = requests.head(doc.path_or_url, allow_redirects=True, timeout=5)
                    if response.status_code == 200:
                        sources.append(Source(doc.path_or_url))
                    else:
                        warnings.warn(f"URL '{doc.path_or_url}' returned status code {response.status_code}.")
                except requests.RequestException as e:
                    warnings.warn(f"Failed to access URL '{doc.path_or_url}': {e}")
            else:
                warnings.warn(f"Invalid path or URL: {doc.path_or_url}")

        if sources:
            # Auto generate graph ontology if not created by user.
            if self.ontology is None:
                self.ontology = Ontology.from_sources(
                    sources=sources,
                    model=self.model,
                )

            self.knowledge_graph = KnowledgeGraph(
                name=self.name,
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                model_config=KnowledgeGraphModelConfig.with_model(self.model),
                ontology=self.ontology,
            )

            self.knowledge_graph.process_sources(sources)

            # Establishing a chat session will maintain the history
            self._chat_session = self.knowledge_graph.chat_session()

            # Save Ontology to graph for future access.
            self._save_ontology_to_db(self.name, self.ontology)
        else:
            raise ValueError("No input documents could be loaded.")

    def add_records(self, new_records: List) -> bool:
        raise NotImplementedError("This method is not supported by FalkorDB SDK yet.")

    def query(self, question: str, n_results: int = 1, **kwargs) -> GraphStoreQueryResult:
        """
        Query the knowledge graph with a question and optional message history.

        Args:
        question: a human input question.
        n_results: number of returned results.
        kwargs:
            messages: a list of message history.

        Returns: FalkorGraphQueryResult
        """
        if self.knowledge_graph is None:
            raise ValueError("Knowledge graph has not been selected or created.")

        response = self._chat_session.send_message(question)

        # History will be considered when querying by setting the last_answer
        self._chat_session.last_answer = response["response"]

        return GraphStoreQueryResult(answer=response["response"], results=[])
    
    def __get_ontology_storage_graph(self, graph_name: str) -> Graph:
        ontology_table_name = graph_name + "_ontology"
        return self.falkordb.select_graph(ontology_table_name)

    def _save_ontology_to_db(self, graph_name: str, ontology: Ontology):
        """
        Save graph ontology to a separate table with {graph_name}_ontology
        """
        graph = self.__get_ontology_storage_graph(graph_name)
        ontology.save_to_graph(graph)

    def _load_ontology_from_db(self, graph_name: str) -> Ontology:
        graph = self.__get_ontology_storage_graph(graph_name)
        return Ontology.from_graph(graph)
