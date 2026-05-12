import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/response_generator/docs',
    component: ComponentCreator('/response_generator/docs', 'c58'),
    routes: [
      {
        path: '/response_generator/docs',
        component: ComponentCreator('/response_generator/docs', '35c'),
        routes: [
          {
            path: '/response_generator/docs',
            component: ComponentCreator('/response_generator/docs', '2c2'),
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
                path: '/response_generator/docs/how-it-works',
                component: ComponentCreator('/response_generator/docs/how-it-works', 'd22'),
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
