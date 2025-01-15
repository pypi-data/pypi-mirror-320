# textToKnowledgeGraph

A Python package to generate BEL statements and CX2 networks.

## Table of Contents

- [License](#license)
- [Project Description](#project-description)
- [Glossary](#glossary)
- [Installation](#installation)
- [Methodology](#methodology)
  - [BEL Generation](#bel-generation)
  - [CX2 Network Generation](#cx2-network-generation)
  - [Uploading to NDEx](#uploading-to-ndex)
- [Usage](#usage)

## License

## Project Description

`textToKnowledgeGraph` is a Python package that converts natural language scientific text into structured knowledge graphs using the capabilities of advanced language models (LLMs). It can be used for:

- Generating BEL statements.
- Extracting entities and interactions from scientific text.
- Uploading the generated CX2 networks to NDEx.

## Glossary

These discusses terms that would be used in this documentation:

- BEL (Biological Expression Language): BEL is a structured language used to represent scientific findings, especially in the biomedical domain, in a computable format. Learn More: [BEL Documentation](https://language.bel.bio/)
- CX2 (Cytoscape Exchange Format 2): CX2 is a JSON-based format used for storing and exchanging network data in Cytoscape. Learn More: [CX2 Specification](http://manual.cytoscape.org/en/stable/Supported_Network_File_Formats.html#cx2)
- PMCID (PubMed Central Identifier): A unique identifier for articles archived in PubMed Central (PMC), a free digital repository of biomedical and life sciences journal literature. Learn More: [PubMed Central](https://www.ncbi.nlm.nih.gov/pmc/)
- NDEx (Network Data Exchange): NDEx is an online resource that facilitates the sharing, storage, and visualization of biological networks. Learn More: [NDEx](https://www.ndexbio.org)
- LangChain: LangChain is a framework for developing applications powered by language models. It allows easy integration of language models with data sources and APIs, enabling workflows like knowledge extraction and retrieval. 
Learn More: [LangChain](https://python.langchain.com/docs/introduction/)
- Cytoscape: Cytoscape is an open-source platform for visualizing and analyzing complex networks, including biological pathways, protein interaction networks, and more. Learn More: [Cytoscape](https://cytoscape.org)
- Knowledge Graph: A knowledge graph is a structured representation of knowledge in a graph format, where entities are nodes and relationships are edges. It enables intuitive querying, reasoning, and visualization of complex biological data, aiding in understanding biological systems and facilitating discoveries.

## Installation

Install the package via pip:

```bash
pip install textToKnowledgeGraph
```

## Methodology

- ## BEL Generation

  - The `process_paper` function in [`textToKnowledgeGraph.main`](textToKnowledgeGraph/main.py) processes scientific papers with PMCIDs to extract biological interactions and generate BEL statements.
  - The `llm_bel_processing` function in [`textToKnowledgeGraph.sentence_level_extraction`](textToKnowledgeGraph/sentence_level_extraction.py) performs sentence-level extraction of BEL statements using openai model. It passes the papers through the language model to extract BEL statements paragraph by paragraph. Then it saves the extracted BEL statements with the paragraph that it was extracted from.  

- ## CX2 Network Generation

  - The `convert_to_cx2` function in [`textToKnowledgeGraph.convert_to_cx2`](textToKnowledgeGraph/convert_to_cx2.py) converts extracted interactions into CX2 network format for visualization in Cytoscape.

<!-- - **Prompt Handling**:
  - The `get_prompt` function in [`textToKnowledgeGraph.get_interactions`](textToKnowledgeGraph/get_interactions.py) reads and processes prompt files to generate prompts for language models.

- **Chain Initialization**:
  - The `initialize_chains` function in [`textToKnowledgeGraph.get_interactions`](textToKnowledgeGraph/get_interactions.py) initializes extraction chains using the provided API key for interaction extraction. -->

- ## Uploading to NDEx

  - The `save_new_cx2_network` function in [`textToKnowledgeGraph.main`](textToKnowledgeGraph/main.py) uploads the generated CX2 networks to NDEx for sharing and visualization. In order to use this function, you need to provide your NDEx email and password as an argument.

<!-- - **Model Workflow**:
  - The model processes scientific papers to extract biological interactions.
  - It uses language models to perform sentence-level extraction of BEL statements.
  - Extracted interactions are converted into CX2 network format.
  - Prompts are generated and processed to guide the extraction process.
  - Extraction chains are initialized using an API key.
  - Generated networks are uploaded to NDEx for visualization and sharing. -->

## Usage

To install python package:

```bash
pip install textToKnowledgeGraph
```

**Required parameters**:

- **pmc_id**: can only process one at a time

- **api_key**: open_ai api key

**Optional parameters**:

- **ndex_email**: The NDEx email for authentication. ndex_password: The NDEx password for authentication.

**Expected output**:

- **BEL statements**: extracted from the paper
- **CX2 network**: generated from the extracted BEL statements

To run in an interactive python environment:

```python
# Process pmcid without uploading to ndex
from textToKnowledgeGraph import process_paper
 
process_paper("PMC8354587","sk-....") 

# Process pmcid and upload to ndex

from textToKnowledgeGraph import process_paper

process_paper("PMC8354587","sk-..", "favour.ujames196@gmail.com", "Fujames17", upload_to_ndex=True)
```
