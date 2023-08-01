import argparse
import re
from textwrap import indent
from typing import Any, Dict, Match
import yaml
import mistune
from mistune import BlockState, Markdown, InlineState
from mistune.renderers.markdown import MarkdownRenderer
from mistune.plugins import math, formatting

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
        print(token)
        if (
            token["type"] == "list" and not self.flag
        ):  # only when token < 20 and not have flag
            self.flag = True
            return "\n<!--truncate-->\n" + func(token, state)
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
            count = re.findall(r":+", body)
            dot_ = max(count, key=len) + ":" if count else ":" * 3
            return dot_ + alias + match.group(3) + body + f"\n{dot_}\n"
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

    def mark(self, token: Dict[str, Any], state: InlineState) -> str:
        return "<Highlight>" + self.render_children(token, state) + "</Highlight>"


class MyBlockParser(mistune.BlockParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def parse_block_quote(self, m: Match, state: BlockState) -> int:
        """Parse token for block quote. Here is an example of the syntax:

        .. code-block:: markdown

            > a block quote starts
            > with right arrows
        """
        text, end_pos = self.extract_block_quote(m, state)
        # scan children state
        child = state.child_state(text)

        if state.depth() >= self.max_nested_level - 1:
            rules = list(self.block_quote_rules)
            rules.remove("block_quote")
        else:
            rules = self.block_quote_rules

        self.parse(child, rules)
        token = {"type": "block_quote", "children": child.tokens}
        if end_pos:
            state.prepend_token(token)
            return end_pos
        state.append_token(token)
        return state.cursor


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


def parse_show_link(inline, m, state):
    """
    Parse link.

    ```markdown
    ![[link]]
    ![[link|text]]
    ```
    """
    text = m.group(0)
    pos = m.end()
    match = re.match(r"!\[\[(.*)\]\]", text)
    if match:
        link = match.group(1)
        if "|" in link:
            link, text = link.split("|", 1)
        else:
            text = ""
        state.append_token(
            {
                "type": "image",
                "children": [{"type": "text", "raw": text}],
                "attrs": {"url": link},
            }
        )
    return pos


def show_link(md):
    md.block.register("show_link", r"!\[\[.*?\]\]", parse_show_link)
    md.inline.register("show_link", r"!\[\[.*?\]\]", parse_show_link)


def show_link_in_list(md):
    """Enable show_link plugin in list."""
    md.block.insert_rule(md.block.list_rules, "show_link", before="list")


def main(args):
    if args.output is None:
        args.output = args.input.replace(".md", ".mdx")
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    renderer = MyRenderer()
    markdown = Markdown(
        renderer=renderer,
        block=MyBlockParser(),
        plugins=[
            math.math,
            math.math_in_quote,
            math.math_in_list,
            plugin_front_matters,
            formatting.mark,
            show_link,
            show_link_in_list,
        ],
    )
    text = markdown(text)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    args = parse_args()
    main(args)
