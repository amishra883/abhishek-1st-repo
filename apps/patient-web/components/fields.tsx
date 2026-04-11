"use client";

import { ChangeEvent } from "react";

export type FieldProps<T> = {
  id: string;
  label: string;
  value: T;
  onChange: (value: T) => void;
  required?: boolean;
};

export function SingleSelectField({
  id,
  label,
  value,
  onChange,
  options,
  required,
}: FieldProps<string> & { options: string[] }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <label htmlFor={id}>{label}</label>
      <select
        id={id}
        value={value ?? ""}
        required={required}
        onChange={(e: ChangeEvent<HTMLSelectElement>) => onChange(e.target.value)}
      >
        <option value="" disabled>
          Select
        </option>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </div>
  );
}

export function MultiSelectField({
  id,
  label,
  value,
  onChange,
  options,
}: FieldProps<string[]> & { options: string[] }) {
  const current = value ?? [];
  const toggle = (opt: string, checked: boolean) => {
    if (checked) onChange([...current, opt]);
    else onChange(current.filter((x) => x !== opt));
  };
  return (
    <div style={{ marginBottom: 16 }}>
      <label>{label}</label>
      {options.map((opt) => (
        <label key={opt} style={{ display: "block" }}>
          <input
            type="checkbox"
            checked={current.includes(opt)}
            onChange={(e) => toggle(opt, e.target.checked)}
          />
          {opt}
        </label>
      ))}
    </div>
  );
}

export function ScaleField({
  id,
  label,
  value,
  onChange,
  min = 1,
  max = 10,
  required,
}: FieldProps<number> & { min?: number; max?: number }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        type="number"
        min={min}
        max={max}
        required={required}
        value={Number.isFinite(value) ? value : ""}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </div>
  );
}
