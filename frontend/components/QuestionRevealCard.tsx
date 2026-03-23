"use client";

type QuestionRevealCardProps = {
  prompt: string;
  answer: string;
  onScore: () => void;
};

export function QuestionRevealCard({ prompt, answer, onScore }: Readonly<QuestionRevealCardProps>) {
  return (
    <section className="rounded-2xl border border-amber-300/50 bg-amber-100/70 p-4 shadow-lg backdrop-blur-sm">
      <p className="text-xs font-semibold uppercase tracking-widest text-amber-700">Q&A Reveal</p>
      <h3 className="mt-2 text-lg font-semibold text-amber-950">{prompt}</h3>
      <p className="mt-3 rounded-xl bg-white/70 p-3 text-sm text-amber-900">{answer}</p>
      <button
        type="button"
        onClick={onScore}
        className="mt-4 w-full rounded-xl bg-amber-600 px-4 py-2 font-semibold text-white transition hover:bg-amber-500"
      >
        Score Another Player
      </button>
    </section>
  );
}
