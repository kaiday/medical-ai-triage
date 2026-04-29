interface PainScaleProps {
  value: number | null;
  onChange: (value: number) => void;
}

export function PainScale({ value, onChange }: PainScaleProps) {
  return (
    <fieldset>
      <legend className="mb-3 text-base font-bold text-ink-900">Pain level</legend>
      <div className="grid grid-cols-5 gap-2 sm:grid-cols-10">
        {Array.from({ length: 10 }, (_, index) => index + 1).map((level) => {
          const selected = value === level;
          return (
            <button
              aria-pressed={selected}
              className={`grid min-h-14 place-items-center rounded-xl border text-base font-bold transition ${
                selected
                  ? 'border-brand-700 bg-brand-700 text-white shadow-soft'
                  : 'border-clinic-border bg-white text-ink-700 hover:border-brand-500 hover:bg-brand-50'
              }`}
              key={level}
              onClick={() => onChange(level)}
              type="button"
            >
              {level}
            </button>
          );
        })}
      </div>
      <div className="mt-2 flex justify-between text-xs font-medium text-ink-500">
        <span>No pain</span>
        <span>Worst pain</span>
      </div>
    </fieldset>
  );
}
