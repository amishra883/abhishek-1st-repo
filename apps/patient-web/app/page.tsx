import Link from "next/link";

const COMPLAINTS = [
  { id: "chest_pain", label: "Chest Pain" },
  { id: "urinary_symptoms", label: "Urinary Symptoms" },
];

export default function HomePage() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Smart Intake</h1>
      <p>Select your chief complaint to begin.</p>
      <ul>
        {COMPLAINTS.map((c) => (
          <li key={c.id}>
            <Link href={`/intake/${c.id}`}>{c.label}</Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
