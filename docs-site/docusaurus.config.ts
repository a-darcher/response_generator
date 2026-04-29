import type {Config} from '@docusaurus/types';

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
        {to: '/', label: 'Demos', position: 'left'},
        {to: '/docs/intro', label: 'Docs', position: 'left'},
        {
          href: 'https://github.com/a-darcher/response_generator',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
  },
};


export default config;