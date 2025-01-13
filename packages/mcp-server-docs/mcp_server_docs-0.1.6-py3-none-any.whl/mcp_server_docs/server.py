from textwrap import dedent

import json
import mcp.types as types
from mcp.server import Server
import mcp.server.stdio

from pydantic.networks import AnyUrl
from mcp_server_docs import explorer

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

                    Example:
                    Fetch API documentation:
                        {
                            "repository": "Anthropic documentation",
                            "path": "docs/api/messages/messages"
                        }
                    """.strip()),
                inputSchema={
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
                    },
                    "required": ["repository", "path"]
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
            ),
            types.Tool(
                name="search-documents",
                description=dedent("""\
                    Search through documentation using either content-based
                     search or path patterns.

                    The tool supports two search modes:
                    1. Content search: Uses regex patterns to search through
                     document contents
                    2. Path pattern search: Uses glob patterns to find
                     documents by path

                    Content search features:
                    - Case-sensitive/insensitive search
                    - Search specific fields (title, content, description)
                    - Regular expression support
                    Path pattern examples:
                    - "**/*.md" - All markdown files
                    - "api/**" - All files under api directory
                    - "docs/guides/*" - Direct children of guides directory
                    """.strip()),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": dedent("""\
                            Search query (regex for content search, glob
                             pattern for path search)""")
                        },
                        "search_type": {
                            "type": "string",
                            "enum": ["content", "pattern"],
                            "description": "Type of search to perform",
                            "default": "content"
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "description": dedent("""\
                            Whether to perform case-sensitive search (content
                             search only)"""),
                            "default": False
                        },
                        "search_fields": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["title", "content", "description"]
                            },
                            "description": dedent("""\
                            Fields to search in (content search only). If
                             empty, searches all fields."""),
                        }
                    },
                    "required": ["query"]
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

            repository = arguments.get("repository")
            doc_path = arguments.get("path")

            if not repository or not doc_path:
                return [types.TextContent(
                    type="text",
                    text="Error: Missing repository or path parameter"
                )]

            if doc := doc_explorer.get(repository=repository, path=doc_path):
                content = f"# {doc.title}\n\n"
                if doc.description:
                    content += f"{doc.description}\n\n"
                content += doc.content
                return [types.TextContent(
                    type="text",
                    text=content
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"""Document not found: {json.dumps(
                        arguments,
                        indent=2
                        )
                        }"""
                )]

        elif name == "list-repositories":
            return [
                types.TextContent(
                    type="text",
                    text="\n".join(VALID_REPOSITORIES)
                )
            ]

        elif name == "search-documents":
            if not arguments:
                raise ValueError("Missing arguments")

            query = arguments.get("query")
            if not query:
                return [types.TextContent(
                    type="text",
                    text="Error: Missing query parameter"
                )]

            search_type = arguments.get("search_type", "content")
            case_sensitive = bool(
                arguments.get("case_sensitive", "").lower() == "true"
                )
            search_fields = arguments.get("search_fields", [])
            if isinstance(search_fields, str):
                search_fields = [
                    field.strip() for field in search_fields.split(",")
                    ]
            search_fields = set(search_fields)

            # Perform search based on type
            if search_type == "content":
                results = await doc_explorer.search_content(
                    query=query,
                    case_sensitive=case_sensitive,
                    search_fields=search_fields or None,
                )
            else:  # pattern search
                results = doc_explorer.search_by_pattern(query)

            if not results:
                return [types.TextContent(
                    type="text",
                    text=f"No documents found matching the search: {query}"
                )]

            # Format results
            results_text = f"Found {len(results)} matching documents:\n\n"
            output = [types.TextContent(type="text", text=results_text)]
            for doc_key, doc in results:
                content = "<document>\n"
                content += f'<repository>{doc_key.repository}</repository>\n'
                content += f'<document_path>{doc_key.path}</document_path>\n'
                content += f'<document_title>{doc.title}</document_title>\n'
                if doc.description:
                    content += f"{doc.description}\n"
                content += "</document>\n"
                output.append(types.TextContent(type="text", text=content))

            return output

        else:
            raise ValueError(f"Unknown tool: {name}")

    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
