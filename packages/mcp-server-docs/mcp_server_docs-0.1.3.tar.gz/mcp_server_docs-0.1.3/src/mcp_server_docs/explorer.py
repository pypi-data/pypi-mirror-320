import aiofiles
import asyncio
import re
from pathlib import Path
from dataclasses import dataclass
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a parsed documentation file with structured content."""
    title: str
    content: str
    repository: str
    description: str | None = None
    links: set[str] | None = None

    def __post_init__(self):
        # Initialize empty set if links is None
        if self.links is None:
            self.links = set()

        # Basic validation
        if not self.title:
            raise ValueError("Document must have a title")

    def __str__(self) -> str:
        content_preview = (
            self.content[:100] + "..."
            if len(self.content) > 100 else self.content
        )
        desc_str = f", description: {self.description}" \
            if self.description else ""
        links_str = f", links: {self.links}" \
            if self.links else ""
        return (
            f"Document(title: {self.title}, "
            f"repository: {self.repository}"
            f"{desc_str}{links_str}, content: {content_preview}"
        )


@dataclass(frozen=True, kw_only=True)
class DocumentKey:
    repository: str
    path: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DocumentKey):
            return NotImplemented
        return self.repository == other.repository and self.path == other.path


class DocumentationFileExplorer:
    def __init__(
        self,
        root_paths: dict[str, str],
        valid_file_types: set[str] | None = None,
        skip_dirs: set[str] | None = None,
    ):
        self.root_paths = {
            name: Path(path) for name, path in root_paths.items()
        }
        self.documents: dict[DocumentKey, Document] = {}
        self.skip_dirs = skip_dirs or {
            "docs-old", "prompt-library", "admin-api"
        }
        self.valid_file_types = valid_file_types or {"md", "mdx"}

    def _document_key(
        self, file_path: Path | str, repository: str
    ) -> DocumentKey:
        return DocumentKey(path=str(file_path), repository=repository)

    def get(self, repository: str, path: str) -> Document | None:
        key = self._document_key(
            repository=repository,
            file_path=path
        )
        return self.documents.get(key, None)

    async def crawl_documents(self):
        """
        Asynchronously crawl through directories starting from each root_path
        and collect documents with valid file extensions. Stores results in
        self.documents with paths (without extension) as keys and file contents
        as values.
        """
        tasks = []
        for repo_name, root_path in self.root_paths.items():
            # Create tasks for processing each file
            for file_path in root_path.rglob("*"):
                tasks.append(
                    self._parse_document(file_path, repo_name, root_path)
                )

        # Run all parse tasks concurrently
        await asyncio.gather(*tasks)

    def _extract_frontmatter(self, content: str) -> tuple[dict, str]:
        """Extract YAML frontmatter from markdown content if present."""
        frontmatter = {}
        main_content = content

        # Check for frontmatter between --- markers
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    # Parse YAML frontmatter
                    frontmatter = yaml.safe_load(parts[1])
                    main_content = parts[2].strip()
                except yaml.YAMLError as e:
                    logger.error(f"Error parsing frontmatter: {e}")

        return frontmatter, main_content

    def _extract_title_and_description(
        self, frontmatter: dict, content: str
    ) -> tuple[str | None, str | None, str]:
        """Extract title and description from frontmatter or content."""
        title = None
        description = None
        remaining_content = content

        # First try to get title and description from frontmatter
        if frontmatter:
            title = frontmatter.get('title') or frontmatter.get('sidebarTitle')
            description = frontmatter.get('description')

        # If no title in frontmatter, try to extract from content
        if not title:
            title, remaining_content = self._extract_first_heading(content)

        # If no description in frontmatter, try to extract from content
        if not description:
            description, remaining_content = self._extract_description(
                remaining_content
            )

        return (
            title,
            description,
            remaining_content
        )

    def _extract_first_heading(self, content: str) -> tuple[str | None, str]:
        """Extract the first heading from markdown content."""
        lines = content.split('\n')
        title = None
        content_start = 0

        for i, line in enumerate(lines):
            # Match both # Heading and Heading\n===== styles
            if line.startswith('# '):
                title = line.lstrip('#').strip()
                content_start = i + 1
                break
            elif i + 1 < len(lines) and set(lines[i + 1]) <= {'='}:
                title = line.strip()
                content_start = i + 2
                break

        remaining_content = '\n'.join(lines[content_start:]).strip()
        return title, remaining_content

    def _extract_description(self, content: str) -> tuple[str | None, str]:
        """Extract the first paragraph as description."""
        paragraphs = content.split('\n\n')
        description = None
        remaining_content = content

        if paragraphs:
            first_para = paragraphs[0].strip()
            if first_para and not first_para.startswith('#'):
                description = first_para
                remaining_content = '\n\n'.join(paragraphs[1:]).strip()

        return description, remaining_content

    def _extract_links(self, content: str) -> set[str]:
        """Extract internal document links that match our document keys."""
        links = set()

        # Match markdown links [text](path)
        link_matches = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for match in link_matches:
            path = match.group(2)
            # Remove anchor tags and clean path
            path = path.split('#')[0]
            # Remove file extension
            path = re.sub(r'\.(md|mdx)$', '', path)
            # Only add if it's a key in our documents
            # if path in self.documents:
            links.add(path)

        return links

    def _clean_mdx_content(self, content: str) -> str:
        """
        Clean MDX content by:
        1. Removing HTML/JSX tags while preserving their content
        2. Handling basic markdown formatting
        3. Cleaning up whitespace
        """
        # Remove import statements
        content = re.sub(r'^import.*$', '', content, flags=re.MULTILINE)

        # Remove export statements
        content = re.sub(r'^export.*$', '', content, flags=re.MULTILINE)

        # Remove self-closing JSX/HTML tags
        content = re.sub(r'<[^>]+/>', '', content)

        # Remove opening and closing tags while preserving content between them
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'</[^>]+>', '', content)

        # Remove multiple newlines
        content = re.sub(r'\n\s*\n', '\n\n', content)

        # Remove leading/trailing whitespace
        content = content.strip()

        return content

    async def _parse_document(
        self, file_path: Path, repository: str, root_path: Path
    ):
        """Asynchronously parse a single document file."""
        # Skip directories in skip_dirs
        if any(skip_dir in file_path.parts for skip_dir in self.skip_dirs):
            return

        # Skip directories
        if file_path.is_dir():
            return

        # Check if file has valid extension
        file_extension = file_path.suffix.lstrip(".")
        if file_extension not in self.valid_file_types:
            return

        try:
            # Asynchronously read file contents
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()

            # Clean content if it's an MDX file
            if file_extension == "mdx":
                content = self._clean_mdx_content(content)

            # Create key by removing root path prefix and file extension
            relative_path = file_path.relative_to(root_path)
            key = self._document_key(
                file_path=relative_path.with_suffix(''),
                repository=repository
            )

            # Extract document components
            frontmatter, main_content = self._extract_frontmatter(content)
            (
                title,
                description,
                final_content
            ) = self._extract_title_and_description(
                frontmatter, main_content
            )

            # Use filename as title if no heading found
            if not title:
                title = (
                    file_path.stem.replace('-', ' ')
                    .replace('_', ' ')
                    .title()
                )

            # Create document object
            doc = Document(
                title=title,
                content=final_content,
                repository=repository,
                description=description,
                links=self._extract_links(content)
            )

            # Store in documents dictionary
            self.documents[key] = doc

        except Exception as e:
            # Skip files that can't be read
            logger.error(f"Error reading file {file_path}: {e}")
            return
