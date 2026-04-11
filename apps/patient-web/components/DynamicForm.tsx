"use client";

import { useState } from "react";

type Question = {
  id: string;
  type: string;
  label: string;
  options?: string[];
  min?: number;
  max?: number;
  required?: boolean;
};

export default function DynamicForm({
  protocol,
  onSubmit,
}: {
  protocol: { id: string; questions: Question[] };
  onSubmit: (answers: Record<string, any>) => void;
}) {
  const [answers, setAnswers] = useState<Record<string, any>>({});

  const update = (id: string, value: any) => {
    setAnswers((prev) => ({ ...prev, [id]: value }));
  };

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(answers);
      }}
    >
      <h1>{protocol.id}</h1>

      {protocol.questions.map((q) => (
        <div key={q.id} style={{ marginBottom: 16 }}>
          <label>{q.label}</label>

          {q.type === "single_select" && (
            <select onChange={(e) => update(q.id, e.target.value)} defaultValue="">
              <option value="" disabled>Select</option>
              {q.options?.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          )}

          {q.type === "scale" && (
            <input
              type="number"
              min={q.min}
              max={q.max}
              onChange={(e) => update(q.id, Number(e.target.value))}
            />
          )}

          {q.type === "multi_select" && (
            <div>
              {q.options?.map((opt) => (
                <label key={opt} style={{ display: "block" }}>
                  <input
                    type="checkbox"
                    onChange={(e) => {
                      const current = answers[q.id] || [];
                      if (e.target.checked) update(q.id, [...current, opt]);
                      else update(q.id, current.filter((x: string) => x !== opt));
                    }}
                  />
                  {opt}
                </label>
              ))}
            </div>
          )}
        </div>
      ))}

      <button type="submit">Submit</button>
    </form>
  );
}
