import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/api-ref',
    component: ComponentCreator('/api-ref', 'a5e'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '57a'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '230'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', 'c0d'),
            routes: [
              {
                path: '/docs/config',
                component: ComponentCreator('/docs/config', '67f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/getting-started',
                component: ComponentCreator('/docs/getting-started', '2a1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/pipeline',
                component: ComponentCreator('/docs/pipeline', 'e29'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', 'e5f'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
