import { AlertCircle, ArrowLeft, Check, Loader2, Stethoscope } from 'lucide-react';
import type { FormEvent } from 'react';
import { useMemo, useState } from 'react';
import type { PatientIntake } from '../../lib/types';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { StatusChip } from '../ui/StatusChip';
import { PainScale } from './PainScale';

const durations = ['Just started', 'A few hours', 'A few days', 'More than a week'];
const conditionOptions = ['Heart condition', 'Diabetes', 'Asthma', 'Pregnant', 'None of the above'];

interface IntakeFormProps {
  onBack: () => void;
  onSubmitted: (referenceId: string) => void;
}

export function IntakeForm({ onBack, onSubmitted }: IntakeFormProps) {
  const [chiefComplaint, setChiefComplaint] = useState('');
  const [duration, setDuration] = useState(durations[0]);
  const [painScale, setPainScale] = useState<number | null>(null);
  const [age, setAge] = useState('');
  const [conditions, setConditions] = useState<string[]>([]);
  const [touched, setTouched] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const complaintError = touched && chiefComplaint.trim().length < 5;
  const painError = touched && painScale === null;
  const ageError = touched && age.length > 0 && (Number(age) < 0 || Number(age) > 120);
  const canSubmit = chiefComplaint.trim().length >= 5 && painScale !== null && !ageError;

  const selectedSummary = useMemo(() => {
    if (conditions.length === 0) return 'No conditions selected';
    return conditions.join(', ');
  }, [conditions]);

  function toggleCondition(condition: string) {
    if (condition === 'None of the above') {
      setConditions((current) => (current.includes(condition) ? [] : [condition]));
      return;
    }
    setConditions((current) => {
      const withoutNone = current.filter((item) => item !== 'None of the above');
      return withoutNone.includes(condition)
        ? withoutNone.filter((item) => item !== condition)
        : [...withoutNone, condition];
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTouched(true);
    if (!canSubmit || painScale === null) return;
    const intake: PatientIntake = {
      chiefComplaint: chiefComplaint.trim(),
      duration,
      painScale,
      age: age ? Number(age) : undefined,
      conditions,
    };
    setIsSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 700));
    console.info('Patient intake captured for API submission', intake);
    setIsSubmitting(false);
    onSubmitted(`PAT-${Date.now().toString().slice(-5)}`);
  }

  return (
    <Card className="mx-auto mt-10 max-w-5xl overflow-hidden">
      <div className="grid lg:grid-cols-[0.95fr_1.35fr]">
        <aside className="bg-brand-700 p-6 text-white sm:p-8">
          <button className="mb-8 inline-flex items-center gap-2 text-sm font-bold text-white/80 hover:text-white" onClick={onBack} type="button">
            <ArrowLeft size={18} />
            Back to portal
          </button>
          <div className="grid size-16 place-items-center rounded-2xl bg-white/15">
            <Stethoscope size={34} />
          </div>
          <h1 className="mt-6 text-3xl font-bold leading-tight">Tell us what brings you in today</h1>
          <p className="mt-4 text-base font-medium leading-7 text-white/80">
            Use plain words. A nurse will review your information and decide the next step.
          </p>
          <div className="mt-8 rounded-2xl bg-white/10 p-5">
            <p className="text-sm font-bold uppercase tracking-wide text-white/70">Privacy note</p>
            <p className="mt-2 text-sm font-medium leading-6 text-white/80">
              We only ask for the details needed to help the triage team review your situation.
            </p>
          </div>
          <div className="mt-6 rounded-2xl bg-white p-5 text-ink-900">
            <p className="text-sm font-bold text-ink-500">Current form status</p>
            <div className="mt-3">
              <StatusChip tone={canSubmit ? 'green' : 'orange'}>{canSubmit ? 'Ready to submit' : 'In progress'}</StatusChip>
            </div>
            <p className="mt-3 text-sm font-medium text-ink-500">{selectedSummary}</p>
          </div>
        </aside>
        <form className="space-y-7 p-6 sm:p-8" onSubmit={handleSubmit}>
          <div>
            <label className="text-base font-bold text-ink-900" htmlFor="chiefComplaint">
              What brings you in today?
            </label>
            <textarea
              className={`mt-3 min-h-36 w-full resize-none rounded-2xl border bg-white p-4 text-base font-medium leading-7 text-ink-900 outline-none transition placeholder:text-ink-400 ${
                complaintError ? 'border-coral-500 ring-4 ring-coral-50' : 'border-clinic-border focus:border-brand-500 focus:ring-4 focus:ring-brand-50'
              }`}
              id="chiefComplaint"
              maxLength={500}
              minLength={5}
              onBlur={() => setTouched(true)}
              onChange={(event) => setChiefComplaint(event.target.value)}
              placeholder="Example: I have a terrible headache and I feel dizzy"
              value={chiefComplaint}
            />
            <div className="mt-2 flex items-center justify-between gap-3">
              {complaintError ? (
                <p className="flex items-center gap-2 text-sm font-semibold text-coral-600">
                  <AlertCircle size={16} />
                  Please describe your symptoms in at least 5 characters.
                </p>
              ) : (
                <p className="text-sm font-medium text-ink-500">Plain language is perfect. No medical terms needed.</p>
              )}
              <span className="text-xs font-bold text-ink-400">{chiefComplaint.length}/500</span>
            </div>
          </div>
          <fieldset>
            <legend className="mb-3 text-base font-bold text-ink-900">How long has this been happening?</legend>
            <div className="grid gap-2 sm:grid-cols-4">
              {durations.map((option) => {
                const selected = duration === option;
                return (
                  <button
                    aria-pressed={selected}
                    className={`min-h-12 rounded-xl border px-3 text-sm font-bold transition ${
                      selected ? 'border-brand-700 bg-brand-700 text-white shadow-soft' : 'border-clinic-border bg-white text-ink-700 hover:border-brand-500'
                    }`}
                    key={option}
                    onClick={() => setDuration(option)}
                    type="button"
                  >
                    {option}
                  </button>
                );
              })}
            </div>
          </fieldset>
          <div>
            <PainScale onChange={setPainScale} value={painScale} />
            {painError ? (
              <p className="mt-2 flex items-center gap-2 text-sm font-semibold text-coral-600">
                <AlertCircle size={16} />
                Please select a pain level.
              </p>
            ) : null}
          </div>
          <div>
            <label className="text-base font-bold text-ink-900" htmlFor="age">Patient age</label>
            <input
              className={`mt-3 h-14 w-full rounded-2xl border bg-white px-4 text-base font-medium text-ink-900 outline-none transition ${
                ageError ? 'border-coral-500 ring-4 ring-coral-50' : 'border-clinic-border focus:border-brand-500 focus:ring-4 focus:ring-brand-50'
              }`}
              id="age"
              max={120}
              min={0}
              onBlur={() => setTouched(true)}
              onChange={(event) => setAge(event.target.value)}
              placeholder="Example: 45"
              type="number"
              value={age}
            />
            {ageError ? <p className="mt-2 text-sm font-semibold text-coral-600">Age must be between 0 and 120.</p> : null}
          </div>
          <fieldset>
            <legend className="mb-3 text-base font-bold text-ink-900">Known conditions</legend>
            <div className="flex flex-wrap gap-2">
              {conditionOptions.map((condition) => {
                const selected = conditions.includes(condition);
                return (
                  <button
                    aria-pressed={selected}
                    className={`inline-flex min-h-11 items-center gap-2 rounded-full border px-4 text-sm font-bold transition ${
                      selected ? 'border-brand-700 bg-clinic-mint text-brand-800' : 'border-clinic-border bg-white text-ink-700 hover:border-brand-500'
                    }`}
                    key={condition}
                    onClick={() => toggleCondition(condition)}
                    type="button"
                  >
                    {selected ? <Check size={16} /> : null}
                    {condition}
                  </button>
                );
              })}
            </div>
          </fieldset>
          <div className="flex flex-wrap items-center gap-3 border-t border-clinic-border pt-6">
            <Button disabled={isSubmitting} type="submit">
              {isSubmitting ? <Loader2 className="animate-spin" size={18} /> : null}
              {isSubmitting ? 'Submitting' : 'Submit symptoms'}
            </Button>
            <Button onClick={onBack} type="button" variant="secondary">Cancel</Button>
          </div>
        </form>
      </div>
    </Card>
  );
}
