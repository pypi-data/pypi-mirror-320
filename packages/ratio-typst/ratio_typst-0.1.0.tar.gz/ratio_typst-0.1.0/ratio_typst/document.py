"""Document classes and all content generation blocks."""

from collections.abc import Iterable
from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Literal

from pypst import Content, Document, ShowRule
from pypst.renderable import Plain, Renderable
from pypst.utils import Dictionary, Function, String


@dataclass
class Author(Dictionary):
    """Ratio Typst theme author info."""

    name: String | Renderable | str | None = field(default=None, metadata=dict(keep_none=True))
    affiliation: String | Renderable | str | None = field(
        default=None, metadata=dict(keep_none=True)
    )
    contact: String | Renderable | str | None = field(default=None, metadata=dict(keep_none=True))

    def __post_init__(self) -> None:
        self.name = None if self.name is None else String(self.name)
        self.affiliation = None if self.affiliation is None else String(self.affiliation)
        self.contact = None if self.contact is None else String(self.contact)


@dataclass
class Info(Dictionary):
    """Ratio Typst theme document info."""

    title: str | Content | Renderable | None = None
    abstract: str | Content | Renderable | None = None
    authors: list[Author] = field(default_factory=list)
    logo: str | Content | Renderable | None = None
    date: datetime | None = None
    keywords: list[String | str] | None = field(default_factory=list)
    version: String | str | None = None

    def __post_init__(self) -> None:
        self.title = None if self.title is None else Content(self.title)
        self.abstract = None if self.abstract is None else Content(self.abstract)
        self.authors = [Author(x) if isinstance(x, str) else x for x in self.authors]
        self.logo = None if self.logo is None else Content(self.logo)
        self.keywords = [String(x) for x in self.keywords]
        self.version = None if self.version is None else String(self.version)


@dataclass
class Cover(Dictionary):
    """Cover page settings."""

    background: str | Content | Renderable | None = None
    hero: str | Content | Plain | Renderable | None = None


@dataclass
class DocumentBar(Dictionary):
    """Document info header bar options."""

    kind: String = field(default_factory=lambda: String("document"))


@dataclass
class PageBar(Dictionary):
    """Page number footer bar options."""

    kind: String = field(default_factory=lambda: String("page"))


@dataclass
class NavigationBar(Dictionary):
    """Navigation header bar options."""

    kind: String = field(default_factory=lambda: String("navigation"))


@dataclass
class ProgressBar(Dictionary):
    """Progress footer bar options."""

    kind: String = field(default_factory=lambda: String("progress"))


@dataclass
class Kind:
    """Document kinds supported by Ratio theme."""

    value: Literal["report", "slides"] = "report"

    def render(self) -> str:
        """Render the document kind as a string."""
        return String(self.value).render()


@dataclass
class Themed(Function):
    """Ratio Typst `themed(..)` function call."""

    kind: Kind | None = None
    info: Info | None = None
    cover: Cover | None = None
    frontmatter: Content | str | Renderable | None = None
    outline: str | Renderable | None = None
    bibliography: str | Renderable | None = None
    backmatter: Content | str | Renderable | None = None
    header: DocumentBar | NavigationBar | str | Renderable | None = None
    footer: PageBar | ProgressBar | str | Renderable | None = None

    def __post_init__(self):
        self.frontmatter = None if self.frontmatter is None else Content(self.frontmatter)
        self.backmatter = None if self.backmatter is None else Content(self.backmatter)


@dataclass
class Theme(Function):
    """Ratio Typst themed show rule."""

    kind: Kind | None = None
    info: Info | None = None
    cover: Cover | None = None
    frontmatter: str | Renderable | None = None
    outline: str | Renderable | None = None
    bibliography: str | Renderable | None = None
    backmatter: str | Renderable | None = None
    header: DocumentBar | NavigationBar | str | Renderable | None = None
    footer: PageBar | ProgressBar | str | Renderable | None = None

    def render(self) -> str:
        """Renders the theme's show rule."""
        return ShowRule(
            body=Themed(**{field.name: getattr(self, field.name) for field in fields(self)})
        ).render()


@dataclass
class _Variant(Document):
    theme: Theme = field(default_factory=Theme)

    def __post_init__(self) -> None:
        super().__init__([self.theme])

        self.add_import("@local/ratio-theme:0.1.0", ["*"])
        self.add_import(Plain(f"variants.{self.kind.value}"), ["*"])

    def extend(self, elements: Iterable[Renderable]) -> None:
        """Extend this document with extra elements."""
        for element in elements:
            self.add(element)


@dataclass
class Report(_Variant):
    """Represents a Typst document using the Ratio report theme."""

    kind: Kind = field(default_factory=lambda: Kind("report"))


@dataclass
class Slides(_Variant):
    """Represents a Typst document using the Ratio slides theme."""

    kind: Kind = field(default_factory=lambda: Kind("slides"))
