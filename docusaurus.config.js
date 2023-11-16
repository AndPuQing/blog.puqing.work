// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer").themes.github;
const darkCodeTheme = require("prism-react-renderer").themes.dracula;
const math = require('remark-math');
const katex = require('rehype-katex').default;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Stand Alone Complex",
  tagline: "Empoered with knowledge",
  url: "https://blog.puqing.work",
  baseUrl: "/",
  onBrokenLinks: "warn",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/logo.svg",
  organizationName: "AndPuQing", // Usually your GitHub org/user name.
  projectName: "blog.puqing.work", // Usually your repo name.


  presets: [
    [
      "@docusaurus/preset-classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: false,
        blog: {
          showReadingTime: true,
          editUrl: "https://github.dev/AndPuQing/blog.puqing.work/blob/master/",
          blogSidebarTitle: "All posts",
          blogSidebarCount: "ALL",
          remarkPlugins: [math],
          rehypePlugins: [(options) => {
            const instance = katex({
              ...options,
              trust: (context) => ['\\htmlId', '\\href'].includes(context.command),
              macros: {
                "\\eqref": "\\href{###1}{(\\text{#1})}",
                "\\ref": "\\href{###1}{\\text{#1}}",
                "\\label": "\\htmlId{#1}{}\\tag{#1}"
              }
            })
            return instance;
          }],
          admonitions: {
            keywords: ['note', 'abstract', 'info', 'todo', 'tip', 'success',
              'question', 'warning', 'failure', 'danger', 'example', 'quote']
          },
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
        sitemap: {
          ignorePatterns: ['/tags/**', '/blog/tags/**', '/docs/**',],
          filename: 'sitemap.XML',
        },
        gtag: {
          trackingID: "G-KPEKSDZKLJ",
        }
      }),
    ],
  ],

  stylesheets: [
    {
      href: 'https://fastly.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css',
      type: 'text/css',
      integrity:
        'sha384-odtC+0UGzzFL/6PNoE8rX/SPcQDXBJ+uRepguP4QkPCm2LBxH3FA3y+fKSiJ+AmM',
      crossorigin: 'anonymous',
    },
  ],

  plugins: [
    [
      require.resolve("@easyops-cn/docusaurus-search-local"),
      {
        // ... Your options.
        // `hashed` is recommended as long-term-cache of index file is possible.
        hashed: true,
        // For Docs using Chinese, The `language` is recommended to set to:
        // ```
        language: ["en", "zh"],
        // ```
        // When applying `zh` in language, please install `nodejieba` in your project.
        translations: {
          search_placeholder: "Search",
          see_all_results: "See all results",
          no_results: "No results.",
          search_results_for: 'Search results for "{{ keyword }}"',
          search_the_documentation: "Search the documentation",
          count_documents_found: "{{ count }} document found",
          count_documents_found_plural: "{{ count }} documents found",
          no_documents_were_found: "No documents were found",
        },
      },
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: "Blog of PuQing",
        logo: {
          alt: "Logo",
          src: "img/logo.svg",
        },
        items: [
          {
            to: "/blog",
            label: "Blogs",
            position: "left"
          },
          {
            to: "/blog/tags",
            label: "Tags",
            position: "left"
          },
          {
            href: "https://github.com/AndPuQing",
            label: "Me on GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        style: "light",
        links: [
          {
            title: "More",
            items: [
              {
                label: "See me on Github",
                href: "https://github.com/AndPuQing",
              },
              {
                label: "Powered by Docusaurus",
                href: "https://github.com/facebook/docusaurus",
              },
            ],
          },
        ],
        copyright: `<a href="https://github.com/AndPuQing" target="_blank">@PuQing</a> ${new Date().getFullYear()} All rights reserved | <a href="https://beian.miit.gov.cn/" target="_blank">湘ICP备2020018876号</a>`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        defaultMode: 'light'
      },
    }),
};

module.exports = config;