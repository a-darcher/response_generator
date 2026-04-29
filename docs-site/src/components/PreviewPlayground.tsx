import React, {useEffect, useMemo, useRef, useState} from 'react';

type PreviewResponse = {
  ok: boolean;
  image_base64: string | null;
  stats: Record<string, unknown>;
  warnings: string[];
};

const API_BASE =
  process.env.NODE_ENV === 'development'
    ? 'http://127.0.0.1:8000'
    : 'https://response-generator.onrender.com';

function NumberInput({
  label,
  value,
  min,
  max,
  step,
  onChange,
}: {
  label: string;
  value: number;
  min?: number;
  max?: number;
  step?: number;
  onChange: (v: number) => void;
}) {
  return (
    <div style={{marginBottom: '1rem'}}>
      <label style={{display: 'block', marginBottom: 8, fontWeight: 600}}>
        {label}
      </label>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{width: '100%', padding: 6}}
      />
    </div>
  );
}

function Slider({
  label,
  value,
  min,
  max,
  step,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
}) {
  return (
    <div style={{marginBottom: '1rem'}}>
      <label style={{display: 'block', marginBottom: 8, fontWeight: 600}}>
        {label}: {value}
      </label>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{width: '100%'}}
      />
    </div>
  );
}

function Checkbox({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label style={{display: 'block', marginBottom: '1rem'}}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        style={{marginRight: 8}}
      />
      {label}
    </label>
  );
}

export default function PreviewPlayground(): JSX.Element {
  const [baselineFr, setBaselineFr] = useState(5.0);
  const [responseFr, setResponseFr] = useState(20.0);
  const [latency, setLatency] = useState(0.1);
  const [duration, setDuration] = useState(0.2);
  const [baselineT, setBaselineT] = useState(1.0);
  const [stimulusT, setStimulusT] = useState(1.0);
  const [dt, setDt] = useState(0.001);
  const [induceRefractoryPeriod, setInduceRefractoryPeriod] = useState(true);
  const [seed, setSeed] = useState(42);
  const [nTrials, setNTrials] = useState(100);

  const [includeBursts, setIncludeBursts] = useState(false);
  const [burstRateBaseline, setBurstRateBaseline] = useState(1.0);
  const [burstRateResponse, setBurstRateResponse] = useState(2.0);
  const [burstRateFactor, setBurstRateFactor] = useState(1.0);
  const [burstDurationLam, setBurstDurationLam] = useState(20.0);
  const [burstAlpha, setBurstAlpha] = useState(2.0);
  const [burstBeta, setBurstBeta] = useState(2.0);
  const [burstMultiplier, setBurstMultiplier] = useState(2.0);

  const [useBetaShape, setUseBetaShape] = useState(false);
  const [a, setA] = useState(2.0);
  const [b, setB] = useState(5.0);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PreviewResponse | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const abortRef = useRef<AbortController | null>(null);

  const payload = useMemo(
    () => ({
      baseline_fr: baselineFr,
      response_fr: responseFr,
      latency,
      duration,
      baseline_T: baselineT,
      stimulus_T: stimulusT,
      dt,
      induce_refractory_period: induceRefractoryPeriod,
      seed,
      a: useBetaShape ? a : 1.0,
      b: useBetaShape ? b : 1.0,
      include_bursts: includeBursts,
      burst_rate_baseline: burstRateBaseline,
      burst_rate_response: burstRateResponse,
      burst_rate_factor: burstRateFactor,
      burst_duration_lam: burstDurationLam,
      burst_alpha: burstAlpha,
      burst_beta: burstBeta,
      burst_multiplier: burstMultiplier,
      n_trials: nTrials,
    }),
    [
      baselineFr,
      responseFr,
      latency,
      duration,
      baselineT,
      stimulusT,
      dt,
      induceRefractoryPeriod,
      seed,
      useBetaShape,
      a,
      b,
      includeBursts,
      burstRateBaseline,
      burstRateResponse,
      burstRateFactor,
      burstDurationLam,
      burstAlpha,
      burstBeta,
      burstMultiplier,
      nTrials,
    ]
  );

  const validationErrorsMemo = useMemo(() => {
    const errs: string[] = [];
    const epsilon = 1e-9;

    if (duration + latency > stimulusT + epsilon) {
      errs.push("Duration exceeds latency + stimulus window");
    }

    if (latency > stimulusT + epsilon) {
    errs.push("Latency cannot exceed stimulus window.");
  }



    return errs;
  }, [duration, latency, stimulusT]);

  useEffect(() => {
    setValidationErrors(validationErrorsMemo);
  }, [validationErrorsMemo]);

  useEffect(() => {
    if (validationErrorsMemo.length > 0) {
      setLoading(false);
      setResult(null);
      setError('Invalid parameter combination.');
      return;
    }

    const timeoutId = window.setTimeout(async () => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setLoading(true);
      setError(null);

      try {
        const res = await fetch(`${API_BASE}/preview`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload),
          signal: controller.signal,
        });

        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || `Request failed with ${res.status}`);
        }

        const data: PreviewResponse = await res.json();
        setResult(data);
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          return;
        }
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [payload, validationErrorsMemo]);

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '380px 1fr',
        gap: '2rem',
        alignItems: 'start',
        height: '90vh',
        overflow: 'hidden',
      }}
    >
      <section
        style={{
          border: '1px solid #ddd',
          borderRadius: 12,
          padding: '1rem',
          maxHeight: '90vh',
          overflowY: 'auto',
          position: 'sticky',
          top: '1rem',
        }}
      >
        <h2>Inputs</h2>

        <NumberInput
          label="Number of trials"
          value={nTrials}
          min={1}
          max={500}
          step={1}
          onChange={setNTrials}
        />

        <Slider
          label="Baseline firing rate"
          value={baselineFr}
          min={0}
          max={50}
          step={0.5}
          onChange={setBaselineFr}
        />

        <Slider
          label="Response firing rate"
          value={responseFr}
          min={0}
          max={100}
          step={0.5}
          onChange={setResponseFr}
        />

        <Slider
          label="Latency (s)"
          value={latency}
          min={0}
          max={1}
          step={0.01}
          onChange={setLatency}
        />

        <Slider
          label="Duration (s)"
          value={duration}
          min={0.01}
          max={2}
          step={0.01}
          onChange={setDuration}
        />

        <Slider
          label="Baseline window T (s)"
          value={baselineT}
          min={0.1}
          max={5}
          step={0.1}
          onChange={setBaselineT}
        />

        <Slider
          label="Stimulus window T (s)"
          value={stimulusT}
          min={0.1}
          max={5}
          step={0.1}
          onChange={setStimulusT}
        />

        {/* <Slider
          label="dt (s)"
          value={dt}
          min={0.0005}
          max={0.02}
          step={0.0005}
          onChange={setDt}
        /> */}

        <NumberInput
          label="Seed"
          value={seed}
          min={0}
          max={1000}
          step={1}
          onChange={setSeed}
        />

        <Checkbox
          label="Induce refractory period"
          checked={induceRefractoryPeriod}
          onChange={setInduceRefractoryPeriod}
        />

        <Checkbox
          label="Use beta-shaped response"
          checked={useBetaShape}
          onChange={setUseBetaShape}
        />

        {useBetaShape && (
          <>
            <Slider
              label="Beta alpha (a)"
              value={a}
              min={0.1}
              max={10}
              step={0.1}
              onChange={setA}
            />
            <Slider
              label="Beta beta (b)"
              value={b}
              min={0.1}
              max={10}
              step={0.1}
              onChange={setB}
            />
          </>
        )}

        <Checkbox
          label="Include bursts"
          checked={includeBursts}
          onChange={setIncludeBursts}
        />

        {includeBursts && (
          <>
            <Slider
              label="Burst rate baseline"
              value={burstRateBaseline}
              min={0}
              max={20}
              step={0.1}
              onChange={setBurstRateBaseline}
            />
            <Slider
              label="Burst rate response"
              value={burstRateResponse}
              min={0}
              max={20}
              step={0.1}
              onChange={setBurstRateResponse}
            />
            <Slider
              label="Burst rate factor"
              value={burstRateFactor}
              min={0.1}
              max={10}
              step={0.1}
              onChange={setBurstRateFactor}
            />
            <Slider
              label="Burst duration λ"
              value={burstDurationLam}
              min={1}
              max={100}
              step={1}
              onChange={setBurstDurationLam}
            />
            <Slider
              label="Burst alpha"
              value={burstAlpha}
              min={0.1}
              max={10}
              step={0.1}
              onChange={setBurstAlpha}
            />
            <Slider
              label="Burst beta"
              value={burstBeta}
              min={0.1}
              max={10}
              step={0.1}
              onChange={setBurstBeta}
            />
            <Slider
              label="Burst multiplier"
              value={burstMultiplier}
              min={1}
              max={10}
              step={0.1}
              onChange={setBurstMultiplier}
            />
          </>
        )}

        <h3 style={{marginTop: '1rem'}}>Payload</h3>
        <pre style={{fontSize: 12, overflowX: 'auto'}}>
          {JSON.stringify(payload, null, 2)}
        </pre>
      </section>

      <section
        style={{
          border: '1px solid #ddd',
          borderRadius: 12,
          padding: '1rem',
          maxHeight: '90vh',
          overflowY: 'auto',
          position: 'sticky',
          top: '1rem',
        }}
      >
        <h2>Generated Response</h2>

        {loading && <p>updating…</p>}

        {error && (
          <div style={{padding: '1rem', border: '1px solid #c33'}}>
            {error}
          </div>
        )}

        {validationErrors.length > 0 && (
          <div style={{padding: '1rem', border: '1px solid #f90', backgroundColor: '#ffe'}}>
            <h3>Validation Warnings</h3>
            <ul>
              {validationErrors.map((err, i) => (
                <li key={i}>{err}</li>
              ))}
            </ul>
          </div>
        )}

        {!error && !result && !loading && validationErrors.length === 0 && <p>Adjust sliders to see output.</p>}

        {result && (
          <>
            {result.image_base64 ? (
              <img
                src={`data:image/png;base64,${result.image_base64}`}
                alt="Preview"
                style={{maxWidth: '100%', borderRadius: 8}}
              />
            ) : (
              <p>No image returned.</p>
            )}

            {/* <h3 style={{marginTop: '1rem'}}>Stats</h3>
            <pre style={{overflowX: 'auto'}}>
              {JSON.stringify(result.stats, null, 2)}
            </pre> */}

            {result.warnings.length > 0 && (
              <>
                <h3>Warnings</h3>
                <ul>
                  {result.warnings.map((warning, i) => (
                    <li key={i}>{warning}</li>
                  ))}
                </ul>
              </>
            )}
          </>
        )}
      </section>
    </div>
  );
}