import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/response_generator/__docusaurus/debug',
    component: ComponentCreator('/response_generator/__docusaurus/debug', '1fa'),
    exact: true
  },
  {
    path: '/response_generator/__docusaurus/debug/config',
    component: ComponentCreator('/response_generator/__docusaurus/debug/config', '264'),
    exact: true
  },
  {
    path: '/response_generator/__docusaurus/debug/content',
    component: ComponentCreator('/response_generator/__docusaurus/debug/content', '2fb'),
    exact: true
  },
  {
    path: '/response_generator/__docusaurus/debug/globalData',
    component: ComponentCreator('/response_generator/__docusaurus/debug/globalData', 'fc8'),
    exact: true
  },
  {
    path: '/response_generator/__docusaurus/debug/metadata',
    component: ComponentCreator('/response_generator/__docusaurus/debug/metadata', 'dd7'),
    exact: true
  },
  {
    path: '/response_generator/__docusaurus/debug/registry',
    component: ComponentCreator('/response_generator/__docusaurus/debug/registry', 'a31'),
    exact: true
  },
  {
    path: '/response_generator/__docusaurus/debug/routes',
    component: ComponentCreator('/response_generator/__docusaurus/debug/routes', 'e4e'),
    exact: true
  },
  {
    path: '/response_generator/api-ref',
    component: ComponentCreator('/response_generator/api-ref', '510'),
    exact: true
  },
  {
    path: '/response_generator/docs',
    component: ComponentCreator('/response_generator/docs', 'ca1'),
    routes: [
      {
        path: '/response_generator/docs',
        component: ComponentCreator('/response_generator/docs', 'c6f'),
        routes: [
          {
            path: '/response_generator/docs',
            component: ComponentCreator('/response_generator/docs', 'f3d'),
            routes: [
              {
                path: '/response_generator/docs/config',
                component: ComponentCreator('/response_generator/docs/config', '617'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/response_generator/docs/getting-started',
                component: ComponentCreator('/response_generator/docs/getting-started', '6d0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/response_generator/docs/intro',
                component: ComponentCreator('/response_generator/docs/intro', '1df'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/response_generator/docs/pipeline',
                component: ComponentCreator('/response_generator/docs/pipeline', '1b1'),
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
    path: '/response_generator/',
    component: ComponentCreator('/response_generator/', '5d6'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
