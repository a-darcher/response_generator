import type {Config} from '@docusaurus/types';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

const config: Config = {
  title: 'Response Stats',
  tagline: 'Docs and interactive preview',
  favicon: 'img/favicon.ico',

  url: 'https://a-darcher.github.io',
  baseUrl: '/response_generator/',

  organizationName: 'a-darcher',
  projectName: 'response_generator',

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: 'docs',
          sidebarPath: './sidebars.ts',
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex],
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Response Generator',
      items: [
        {to: '/', label: 'Demo', position: 'left'},
        {to: '/docs/how-it-works', label: 'How it works', position: 'left'},
        {to: '/docs/intro', label: 'Docs', position: 'left'},
        {
          href: 'https://github.com/a-darcher/response_generator',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
  },

  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css',
      type: 'text/css',
      crossOrigin: 'anonymous',
    },
  ],
};

export default config;