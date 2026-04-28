import React from 'react';
import Layout from '@theme/Layout';
import PreviewPlayground from '@site/src/components/PreviewPlayground';

export default function Home(): JSX.Element {
  return (
    <Layout title="Response Stats Playground" description="Interactive preview">
      <main style={{maxWidth: 1000, margin: '0 auto', padding: '2rem 1rem'}}>
        <h1>Generate response rasters</h1>
        <p>Parameters used to generate response rasters. Adjust any and see the effect on the generated response.</p>
        <PreviewPlayground />
      </main>
    </Layout>
  );
}