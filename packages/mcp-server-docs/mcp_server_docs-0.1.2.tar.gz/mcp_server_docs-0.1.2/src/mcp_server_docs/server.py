from textwrap import dedent

import json
import mcp.types as types
from mcp.server import Server
import mcp.server.stdio

from pydantic.networks import AnyUrl
from . import explorer

server = Server(
    "mcp-server-docs",
)


async def serve(repositories: dict[str, str]) -> None:
    # Create DocumentExplorer instance
    doc_explorer = explorer.DocumentationFileExplorer(
        root_paths=repositories
    )
    await doc_explorer.crawl_documents()

    # Dynamically create enum from document keys
    VALID_DOCUMENT_PATHS = list(doc_explorer.documents.keys())
    VALID_REPOSITORIES = list(doc_explorer.root_paths.keys())

    # Schema descriptions
    REPOSITORY_DESCRIPTION = dedent("""\
        Name of the documentation repository

        Examples:
        - "anthropic-documentation"
        - "mcp"
        - "anthropic-sdk-python"
        - "anthropic-sdk-typescript"
        """.strip())

    @server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        """List all available documentation resources."""
        resources = []
        for document_key, doc in sorted(
            doc_explorer.documents.items(),
            key=lambda x: x[1].title
        ):
            resources.append(
                types.Resource(
                    uri=AnyUrl(
                        f"file://{document_key.repository}/"
                        f"{document_key.path}"
                    ),
                    name=(
                        f"[{doc.repository}][{document_key.path}] "
                        f"{doc.title}"
                    ),
                    description=(
                        f"({doc.repository}): "
                        f"{doc.description}"
                    ),
                    mimeType="text/markdown"
                )
            )
        return resources

    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        """Read content from a documentation resource."""
        # Extract path from URI
        uri_str = str(uri)
        if not uri_str.startswith("file://"):
            raise ValueError(f"Invalid URI scheme: {uri}")

        # Remove "file://" prefix
        full_path = uri_str[7:].split('/', maxsplit=1)
        repository, path = full_path[0], full_path[1]
        if doc := doc_explorer.get(repository=repository, path=path):
            content = f"# {doc.title}\n\n"
            if doc.description:
                content += f"{doc.description}\n\n"
            content += doc.content
            return content
        else:
            sorted_docs = sorted(
                doc_explorer.documents.items(),
                key=lambda x: x[1].title
            )
            raise ValueError(
                f"Document not found: ({json.dumps(full_path)})\n"
                f"{sorted_docs}"
            )

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """
        List available tools.
        The fetch-documents tool allows retrieving content from pre-crawled
        documentation.
        """
        return [
            types.Tool(
                name="fetch-documents",
                description=dedent("""\
                    Use this tool to retrieve relevant technical documentation
                    files.
                    This tool can help find and fetch documentation across
                    multiple repositories and topics.

                    The tool will:
                    - Search through available documentation files
                    - Return relevant content based on repository and path
                    - Provide structured documentation with headers

                    Common use cases:
                    - Finding API documentation
                    - Retrieving usage guides and tutorials
                    - Looking up technical specifications
                    - Accessing implementation examples

                    Examples:
                    1. Fetch API documentation:
                        {
                            "documents": [
                            {
                                "repository": "Anthropic documentation",
                                "path": "docs/api/messages/messages"
                            }
                            ]
                        }

                    2. Get both overview and specific feature docs:
                        {
                            "documents": [
                            {
                                "repository": "Model Context Protocol",
                                "path": "docs/concepts/overview"
                            },
                            {
                                "repository": "Model Context Protocol",
                                "path": "docs/concepts/tools"
                            }
                            ]
                        }

                    3. Compare implementation approaches:
                        {
                            "documents": [
                            {
                                "repository": "Python SDK",
                                "path": "docs/implementation/basic-server"
                            },
                            {
                                "repository": "TypeScript SDK",
                                "path": "docs/implementation/basic-server"
                            }
                            ]
                        }
                    """.strip()),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "documents": {
                            "type": "array",
                            "description": dedent("""\
                                A list of document objects to fetch.
                                Each document object must specify:
                                - repository: Documentation repository/category
                                - path: Specific document path

                                Multiple documents can be requested at once.

                                Examples:
                                1. Single document:
                                    {
                                        "documents": [
                                        {
                                            "repository": "Anthropic docs",
                                            "path": "docs/getting-started"
                                        }
                                        ]
                                    }

                                2. Multiple related documents:
                                    {
                                        "documents": [
                                    {
                                        "repository": "MCP",
                                        "path": "docs/concepts/resources"
                                    },
                                    {
                                        "repository": "MCP",
                                        "path": "docs/concepts/tools"
                                    }
                                    ]
                                    }

                                Available repositories: {VALID_REPOSITORIES}
                                """.strip()),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "repository": {
                                        "description": REPOSITORY_DESCRIPTION,
                                        "type": "string",
                                        "enum": VALID_REPOSITORIES,
                                    },
                                    "path": {
                                        "description": dedent("""\
                                            Path to the document

                                            Examples:
                                            - "docs/getting-started"
                                            - "docs/api/messages/messages"
                                            - "docs/concepts/tools"
                                            - "docs/implementation/server"

                                            Common path patterns:
                                            - docs/concepts/... - Concepts
                                            - docs/api/... - API reference
                                            - docs/guides/... - Tutorials
                                            - docs/impl/... - Implementation
                                            """.strip()),
                                        "type": "string",
                                        "enum": VALID_DOCUMENT_PATHS,
                                    }
                                }
                            },
                            "minItems": 1
                        }
                    },
                    "required": ["documents"]
                }
            ),
            types.Tool(
                name="list-repositories",
                description=dedent("""
                Returns a list of all available
                 documentation repositories."""),
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                outputSchema={
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of repository names"
                }
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        Handle tool execution requests.
        """

        if name == "fetch-documents":
            if not arguments:
                raise ValueError("Missing arguments")
            documents = json.loads(arguments["documents"])
            if not documents:
                return [types.TextContent(
                    type="text",
                    text="Error: Missing documents parameter"
                )]

            results = []
            for doc_obj in documents:
                if (
                    (repository := doc_obj.get("repository")) and
                    (doc_path := doc_obj.get("path"))
                ):
                    if doc := doc_explorer.get(repository, doc_path):
                        content = f"# {doc.title}\n\n"
                        if doc.description:
                            content += f"{doc.description}\n\n"
                        content += doc.content
                        results.append(content)
                else:
                    results.append(
                        f"Document not found: {json.dumps(doc_obj, indent=2)}"
                    )

            return [
                types.TextContent(
                    type="text",
                    text="\n\n---\n\n".join(results)
                )
            ]

        elif name == "list-repositories":
            return [
                types.TextContent(
                    type="text",
                    text="\n".join(VALID_REPOSITORIES)
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
