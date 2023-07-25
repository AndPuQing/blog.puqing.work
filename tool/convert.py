import argparse
import re
from textwrap import indent
from typing import Any, Dict, List, Optional
import yaml
import mistune
from mistune import BlockState, Markdown, InlineState
from mistune.renderers.markdown import MarkdownRenderer
from mistune.plugins import math

CALLOUT_BLOCK_REGEX = re.compile(r"\[!([^\]]*)\]([\-\+]?)(.*)?")

META = re.compile(r"^---\n(?P<meta>[\s\S]+?)\n---\n", re.MULTILINE)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file")
    parser.add_argument("-o", "--output", help="output file")
    return parser.parse_args()


class MyRenderer(MarkdownRenderer):
    aliases = {
        "abstract": ["summary", "tldr"],
        "tip": ["hint", "important"],
        "success": ["check", "done"],
        "question": ["help", "faq"],
        "warning": ["caution", "attention"],
        "failure": ["fail", "missing"],
        "danger": ["error"],
        "quote": ["cite"],
    }
    alias_tuples = [
        (alias, c_type) for c_type, aliases in aliases.items() for alias in aliases
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token_number = 0
        self.flag = False

    def render_token(self, token, state):
        self.token_number += 1
        func = self._get_method(token["type"])
        if self.token_number >= 20 and token["type"] == "paragraph" and not self.flag:
            # insert truncated text
            self.flag = True
            return func(token, state) + "\n<!--truncate-->\n"
        return func(token, state)

    def block_quote(self, token: Dict[str, Any], state: BlockState) -> str:
        text = self.render_children(token, state)
        match = CALLOUT_BLOCK_REGEX.match(text)
        if match:
            body = CALLOUT_BLOCK_REGEX.sub("", text)
            body = body[:-1]
            alias_ = match.group(1)
            for alias, c_type in self.alias_tuples:
                if alias == alias_:
                    alias = c_type
                    break
            else:
                alias = alias_
            return ":::" + alias + match.group(3) + body + "\n:::\n"
        else:
            return indent(text, "> ")

    def block_math(self, token: Dict[str, Any], state: BlockState) -> str:
        return "$$\n" + token["raw"] + "\n$$\n"

    def inline_math(self, token: Dict[str, Any], state: InlineState) -> str:
        return "$" + token["raw"] + "$"

    def front_matter(self, token: Dict[str, Any], state: BlockState) -> str:
        meta = token["meta"]
        # tags : tag1, tag2, tag3 -> tags : [tag1, tag2, tag3]
        if "tags" in meta:
            meta["tags"] = [tag.strip() for tag in meta["tags"].split(",")]
        if "author" in meta:
            meta["authors"] = [meta["author"]]
            del meta["author"]
        return "---\n" + yaml.dump(meta, allow_unicode=True) + "---\n"


def parse_front_matters(m: Markdown, state: BlockState):
    """Parse front matters."""

    meta_text, markdown_text = split_front_matter(state.src)
    if meta_text:
        meta = yaml.safe_load(meta_text)
        state.append_token({"type": "front_matter", "meta": meta})
        state.process(markdown_text)


def split_front_matter(s):
    match = META.match(s)
    if match:
        meta_text = match.group(1)
        markdown_text = s[match.end() :]
    else:
        meta_text = ""
        markdown_text = s
    return meta_text, markdown_text


def plugin_front_matters(md: Markdown):
    md.before_parse_hooks.append(parse_front_matters)


def main(args):
    if args.output is None:
        args.output = args.input.replace(".md", ".mdx")
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    renderer = MyRenderer()
    markdown = Markdown(
        renderer=renderer,
        plugins=[
            math.math,
            math.math_in_quote,
            math.math_in_list,
            plugin_front_matters,
        ],
    )
    text = markdown(text)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    args = parse_args()
    main(args)
