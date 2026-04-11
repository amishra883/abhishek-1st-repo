"use client";

import { use, useEffect, useState } from "react";
import DynamicForm from "../../../components/DynamicForm";
import { fetchProtocol, submitIntake, type Protocol } from "../../../lib/protocol";

export default function IntakePage({
  params,
}: {
  params: Promise<{ protocolId: string }>;
}) {
  const { protocolId } = use(params);
  const [protocol, setProtocol] = useState<Protocol | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<unknown>(null);

  useEffect(() => {
    fetchProtocol(protocolId)
      .then(setProtocol)
      .catch((e) => setError(String(e)));
  }, [protocolId]);

  if (error) return <main style={{ padding: 24 }}>Error: {error}</main>;
  if (!protocol) return <main style={{ padding: 24 }}>Loading…</main>;

  return (
    <main style={{ padding: 24 }}>
      <DynamicForm
        protocol={protocol}
        onSubmit={async (answers) => {
          try {
            const data = await submitIntake({
              patient_id: "demo",
              chief_complaint: protocol.label,
              answers,
            });
            setResult(data);
          } catch (e) {
            setError(String(e));
          }
        }}
      />
      {result && (
        <pre style={{ marginTop: 24, whiteSpace: "pre-wrap" }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </main>
  );
}
