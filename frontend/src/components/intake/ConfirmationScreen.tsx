import { CheckCircle2, Clock, Home, Stethoscope } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { StatusChip } from '../ui/StatusChip';

interface ConfirmationScreenProps {
  referenceId: string;
  onBackHome: () => void;
  onNewIntake: () => void;
}

export function ConfirmationScreen({ referenceId, onBackHome, onNewIntake }: ConfirmationScreenProps) {
  return (
    <Card className="mx-auto mt-10 max-w-3xl overflow-hidden">
      <div className="bg-brand-700 px-6 py-8 text-white sm:px-8">
        <div className="mb-5 grid size-16 place-items-center rounded-full bg-white/15">
          <CheckCircle2 size={36} />
        </div>
        <h1 className="text-3xl font-bold">Your information has been received</h1>
        <p className="mt-2 max-w-2xl text-base font-medium text-white/85">
          A nurse will review your symptoms shortly. Please stay nearby and follow any instructions from hospital staff.
        </p>
      </div>
      <div className="space-y-6 p-6 sm:p-8">
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl bg-clinic-green p-4">
            <p className="text-xs font-bold uppercase text-ink-500">Reference</p>
            <p className="mt-2 text-lg font-bold text-ink-900">{referenceId}</p>
          </div>
          <div className="rounded-xl bg-clinic-mint p-4">
            <p className="text-xs font-bold uppercase text-ink-500">Status</p>
            <div className="mt-2">
              <StatusChip tone="mint">Nurse reviewing</StatusChip>
            </div>
          </div>
          <div className="rounded-xl bg-clinic-orange p-4">
            <p className="text-xs font-bold uppercase text-ink-500">Next step</p>
            <p className="mt-2 text-sm font-bold text-ink-900">Wait for nurse call</p>
          </div>
        </div>
        <div className="rounded-xl border border-clinic-border bg-clinic-canvas p-5">
          <div className="flex gap-3">
            <Clock className="mt-0.5 shrink-0 text-brand-700" size={22} />
            <p className="text-sm font-medium leading-6 text-ink-500">
              If your symptoms suddenly get worse, difficulty breathing starts, severe bleeding occurs, or you feel unsafe,
              notify hospital staff immediately.
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button onClick={onBackHome} type="button" variant="teal">
            <Home size={18} />
            Back to portal
          </Button>
          <Button onClick={onNewIntake} type="button" variant="secondary">
            <Stethoscope size={18} />
            Start another intake
          </Button>
        </div>
      </div>
    </Card>
  );
}
