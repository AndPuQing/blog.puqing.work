import argparse
import os
from typing import Dict, Match, Any
import re
import hashlib
import yaml
import mistune
from mistune import BlockState, Markdown, InlineState
from mistune.renderers.markdown import MarkdownRenderer
from mistune.plugins import math, formatting
import coloredlogs
import logging

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")


CALLOUT_BLOCK_REGEX = re.compile(r"\[!([^\]]*)\]([\-\+]?)(.*)?")

META = re.compile(r"^---\n(?P<meta>[\s\S]+?)\n---\n", re.MULTILINE)


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
        self.equation_number = 1

    def render_token(self, token, state):
        # print(token)
        self.token_number += 1
        func = self._get_method(token["type"])
        if (
            token["type"] == "list" and not self.flag
        ):  # only when token < 20 and not have flag
            self.flag = True
            return "\n<!--truncate-->\n" + func(token, state)
        if (
            self.token_number >= 15 and token["type"] == "paragraph" and not self.flag
        ):  # noqa
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
            count = max(count, key=len) + ":" if count else ""
            dot_ = count if len(count) > 3 else ":" * 3
            return dot_ + alias + match.group(3) + body + f"\n{dot_}\n"
        else:
            # 补充::: info
            return ":::info\n" + text + "\n:::\n"

    def block_math(self, token: Dict[str, Any], state: BlockState) -> str:
        # for obsidian math error :(
        # we use \label{} instead of \flat{}
        token["raw"] = token["raw"].replace("\\flat", "\\label")
        return "$$\n" + token["raw"] + "\n$$\n"

    def inline_math(self, token: Dict[str, Any], state: InlineState) -> str:
        return "$" + token["raw"] + "$"

    def front_matter(self, token: Dict[str, Any], state: BlockState) -> str:
        meta = token["meta"]
        # tags : tag1, tag2, tag3 -> tags : [tag1, tag2, tag3]
        if "tags" in meta:
            if isinstance(meta["tags"], str):
                meta["tags"] = meta["tags"].split(", ")
            # remove public/private tag
            meta["tags"] = [
                tag
                for tag in meta["tags"]
                if tag not in ["Public", "Private", "public", "private"]
            ]

        if "creation date" in meta:
            meta["date"] = meta["creation date"]
            del meta["creation date"]
        if "keywords" not in meta:
            meta["keywords"] = meta["tags"].copy()
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


def split_front_matter(s):
    match = META.match(s)
    if match:
        meta_text = match.group(1)
        markdown_text = s[match.end() :]
    else:
        meta_text = ""
        markdown_text = s
    return meta_text, markdown_text


def parse_front_matters(m: Markdown, state: BlockState):
    """Parse front matters."""

    meta_text, markdown_text = split_front_matter(state.src)
    if meta_text:
        meta = yaml.safe_load(meta_text)
        state.append_token({"type": "front_matter", "meta": meta})
        state.process(markdown_text)


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
        if "images" not in link:
            link = "./images/" + link
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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="input dir")
    parser.add_argument("-o", "--output", help="output file")
    return parser.parse_args()


def is_pushlish(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        footmatter_index = 0
        for index, line in enumerate(lines[1:]):
            if line.startswith("---"):
                footmatter_index = index
                break
        if footmatter_index == 0:
            return False
        footmatter = lines[1 : footmatter_index + 1]
        for line in footmatter:
            if "Public" in line or "public" in line:
                return True
    return False


def process_link(file, PUBLISH_DICT: Dict):
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        code_block = False
        for index, line in enumerate(lines):
            # ignore code block
            if line.startswith("```"):
                code_block = not code_block
                continue
            if code_block:
                continue
            regex = re.compile(r"\[\[(.*?)\]\]")
            match = regex.findall(line)

            if not match:
                continue
            for raw in match:
                # [[link#anchor|alias]]
                link, anchor, alias = raw, "", raw
                if "|" in raw:
                    link, alias = raw.split("|", 1)
                else:
                    link = raw
                if "#" in link:
                    link, anchor = link.split("#", 1)
                if link in PUBLISH_DICT:
                    link = hashlib.md5(link.encode("utf-8")).hexdigest()[0:8]
                    if anchor:
                        anchor: str = "#" + anchor
                        anchor = anchor.replace(" ", "-")
                        anchor = anchor.lower()
                    lines[index] = lines[index].replace(
                        f"[[{raw}]]", f"[{alias}](./{link}{anchor})"
                    )
                else:
                    if link == "":
                        anchor: str = "#" + anchor
                        alias = alias.replace("#", "")
                        lines[index] = lines[index].replace(
                            f"[[{raw}]]", f"[{alias}](./{anchor})"
                        )
                        continue
                    logger.warning(f"Can't find {link} in publish list")
                    lines[index] = lines[index].replace(
                        f"[[{raw}]]",
                        f"[{alias}(This page is not published)](./404)",  # noqa
                    )
    return lines


def main(args):
    file_dir = args.dir
    output_dir = args.output

    file_list = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if file.endswith(".md"):
                file_list.append(os.path.join(root, file))

    publish_list = []
    for file in file_list:
        if is_pushlish(file):
            publish_list.append(file)

    PUBLISH_DICT = {}
    for file in publish_list:
        file_name = file.split("/")[-1]
        file_name = file_name.replace(".md", "")
        PUBLISH_DICT[file_name] = file

    for key in PUBLISH_DICT.keys():
        new_file = process_link(PUBLISH_DICT[key], PUBLISH_DICT)
        new_name = hashlib.md5(key.encode("utf-8")).hexdigest()[0:8] + ".mdx"
        render = MyRenderer()
        markdown = Markdown(
            renderer=render,
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
        new_file = markdown("".join(new_file))
        with open(os.path.join(output_dir, new_name), "w", encoding="utf-8") as f:
            f.writelines(new_file)
        logger.info(f"Success convert {key} to {os.path.join(output_dir, new_name)}")


if __name__ == "__main__":
    args = parse_args()
    main(args)
