import React from 'react';
import {useEffect} from 'react';
import useBaseUrl from '@docusaurus/useBaseUrl';

export default function ApiRefRedirect(): JSX.Element {
  const target = useBaseUrl('/api-ref/index.html');

  useEffect(() => {
    window.location.replace(target);
  }, [target]);

  return <p>Redirecting to API Reference…</p>;
}