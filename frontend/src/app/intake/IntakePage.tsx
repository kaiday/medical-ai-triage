import {
  CalendarDays,
  Check,
  ChevronDown,
  ChevronRight,
  Clock3,
  Droplet,
  HeartPulse,
  MapPin,
  MessageCircle,
  Pill,
  Plus,
  Send,
  TestTube2,
  type LucideIcon,
} from 'lucide-react';
import { ReactNode, useState } from 'react';

import { ConfirmationScreen } from '../../components/intake/ConfirmationScreen';
import { IntakeForm } from '../../components/intake/IntakeForm';
import { PatientPortalShell } from '../../components/layout/PatientPortalShell';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { StatusChip } from '../../components/ui/StatusChip';

type PatientPortalView = 'dashboard' | 'intake' | 'confirmation';

const recentConsultations = [
  ['Dr. Alison', 'Practioner', 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=80&q=80'],
  ['Dr. Patel', 'Practioner', 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=80&q=80'],
  ['Dr. Smith', 'Health', 'https://images.unsplash.com/photo-1582750433449-648ed127bb54?auto=format&fit=crop&w=80&q=80'],
  ['Dr. Chen', 'Health', 'https://images.unsplash.com/photo-1594824476967-48c8b964273f?auto=format&fit=crop&w=80&q=80'],
];

const quickActions: Array<[string, string, LucideIcon]> = [
  ['Book an Appointment', 'Find a doctor and specialization', CalendarDays],
  ['Request Consultation', 'Talk to a specialist', MessageCircle],
  ['Locate a hospital near you', 'Find closest hospitals', MapPin],
  ['Emergency', 'Request immediate help', Send],
];

function MetricCard({
  icon,
  title,
  value,
  unit,
  tone,
  children,
}: {
  icon: ReactNode;
  title: string;
  value: string;
  unit: string;
  tone: 'cyan' | 'rose' | 'amber';
  children: ReactNode;
}) {
  const tones = {
    cyan: 'bg-cyan-100 text-teal-700 border-cyan-200',
    rose: 'bg-rose-100 text-rose-600 border-rose-200',
    amber: 'bg-amber-100 text-amber-600 border-amber-200',
  };

  return (
    <Card className="min-h-[234px] overflow-hidden p-5">
      <div className="flex items-start gap-4">
        <div className={`grid h-14 w-14 shrink-0 place-items-center rounded-xl border ${tones[tone]}`}>{icon}</div>
        <h3 className="text-base font-bold leading-snug text-ink-900">{title}</h3>
      </div>
      <div className="mt-5 flex flex-wrap items-end gap-2">
        <span className="text-3xl font-medium leading-none text-ink-900">{value}</span>
        <span className="pb-1 text-sm font-bold text-ink-500">{unit}</span>
      </div>
      <div className="mt-2 flex flex-wrap gap-1.5">
        <StatusChip tone={tone === 'cyan' ? 'mint' : tone === 'rose' ? 'coral' : 'orange'}>Normal</StatusChip>
        <StatusChip>Edit</StatusChip>
      </div>
      <div className="mt-1 h-[70px] overflow-hidden">{children}</div>
    </Card>
  );
}

function Sparkline({ color = '#1897a2' }: { color?: string }) {
  return (
    <svg className="h-full w-full" viewBox="0 0 190 70" preserveAspectRatio="none" aria-hidden="true">
      <path d="M0 58 C20 70 35 57 45 32 C60 0 84 48 107 30 C127 15 134 2 150 34 C166 66 178 9 190 49 L190 70 L0 70 Z" fill={color} opacity="0.12" />
      <path d="M0 58 C20 70 35 57 45 32 C60 0 84 48 107 30 C127 15 134 2 150 34 C166 66 178 9 190 49" fill="none" stroke={color} strokeWidth="1.4" />
    </svg>
  );
}

function AppointmentCard() {
  return (
    <Card className="p-4">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-bold text-ink-900">Upcoming Appointment</h2>
        <button className="text-xs font-medium text-coral-500 underline">View All</button>
      </div>
      <div className="min-h-[158px] rounded-md bg-brand-700 p-5 text-white sm:p-7">
        <div className="grid h-full gap-5 md:grid-cols-[1fr_1.26fr] md:items-center">
          <div className="flex items-center gap-3">
            <div className="relative">
              <img className="h-12 w-12 rounded-full object-cover ring-4 ring-white" alt="" src="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=96&q=80" />
              <span className="absolute -bottom-1 -right-1 grid h-5 w-5 place-items-center rounded-full bg-blue-500 ring-2 ring-brand-700">
                <Check className="h-3 w-3" />
              </span>
            </div>
            <div>
              <p className="font-bold">Dr. Alison Ogaga</p>
              <p className="text-sm text-white/90">General Practioner</p>
            </div>
          </div>
          <div className="space-y-4 md:border-l md:border-white/40 md:pl-6">
            <div className="grid gap-3 text-xs sm:grid-cols-2">
              <span className="flex items-center gap-2"><CalendarDays className="h-4 w-4" /> October 28th, 2023</span>
              <span className="flex items-center gap-2"><Clock3 className="h-4 w-4" /> 11:30 -12:00 (30min)</span>
              <span className="flex items-center gap-2 sm:col-span-2"><MapPin className="h-4 w-4" /> Medicare Hospital, 18 Iwaya Rd, Lagos</span>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button variant="secondary" className="min-h-9 px-4">Reschedule</Button>
              <button className="flex items-center gap-2 text-sm font-bold">
                <span className="grid h-5 w-5 place-items-center rounded-full bg-green-400 text-white">
                  <Check className="h-3 w-3" />
                </span>
                Confirm appointment
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-2 flex justify-center gap-2">
        <span className="h-2 w-4 rounded-full bg-green-500" />
        <span className="h-2 w-2 rounded-full bg-zinc-300" />
        <span className="h-2 w-2 rounded-full bg-zinc-300" />
      </div>
    </Card>
  );
}

function ActivityGrowthCard() {
  return (
    <Card className="p-5">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-bold text-ink-900">Activity Growth</h2>
        <div className="flex flex-wrap items-center gap-3 text-sm text-ink-500">
          <span className="flex items-center gap-1.5"><b className="h-2 w-2 rounded-full bg-coral-500" /> My Weight</span>
          <span className="flex items-center gap-1.5"><b className="h-2 w-2 rounded-full bg-blue-600" /> My BMI Record</span>
          <StatusChip tone="mint"><CalendarDays className="h-4 w-4" /> October 28th, 2023</StatusChip>
        </div>
      </div>
      <svg className="h-52 w-full" viewBox="0 0 620 220" preserveAspectRatio="none" aria-label="Activity growth chart">
        {[35, 70, 105, 140, 175].map((y) => (
          <line key={y} x1="20" x2="610" y1={y} y2={y} stroke="#CBD5E1" strokeDasharray="4 5" />
        ))}
        <path d="M50 150 C95 120 110 155 150 148 C210 136 235 165 270 142 C312 113 310 190 355 114 C392 72 425 150 470 120 C510 94 512 87 540 146 C570 203 592 163 600 64" fill="none" stroke="#1474e8" strokeWidth="3" />
        <path d="M50 158 C100 138 135 154 164 150 C205 145 220 130 260 149 C304 170 318 100 355 142 C388 180 408 110 460 122 C502 135 508 66 540 112 C568 156 585 210 600 44" fill="none" stroke="#ff5f3b" strokeWidth="3" />
      </svg>
    </Card>
  );
}

function RightColumn({ onStartIntake }: { onStartIntake: () => void }) {
  return (
    <div className="space-y-4">
      <Card className="p-5">
        <div className="flex gap-4">
          <div className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-clinic-green text-brand-700"><Pill className="h-5 w-5" /></div>
          <div className="min-w-0 flex-1 text-center">
            <h2 className="font-bold text-ink-900">My Pills Tracker</h2>
            <p className="text-xs text-ink-500">27 October. 2023</p>
            <div className="mt-4 flex flex-wrap gap-2 text-left">
              <StatusChip tone="mint">IN PROGRESS</StatusChip>
              <StatusChip>Edit</StatusChip>
            </div>
            <div className="mt-4 rounded-lg bg-clinic-green p-3 text-left text-xs text-ink-900">
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <p className="font-bold text-coral-500">Expected Delivery Date</p>
                  <p className="mt-2 flex items-center gap-2"><CalendarDays className="h-4 w-4" /> October 28th, 2023</p>
                </div>
                <div>
                  <p className="font-bold text-coral-500">ANC Day</p>
                  <p className="mt-2 flex items-center gap-2"><CalendarDays className="h-4 w-4" /> Tuesday</p>
                </div>
              </div>
              <p className="mt-3 flex items-center gap-2"><MapPin className="h-4 w-4" /> Medicare Hospital, 18 Iwaya Rd, Lagos</p>
            </div>
            <div className="mt-4 border-t pt-4 text-left">
              <Button onClick={onStartIntake} className="min-h-9 px-4"><Plus className="h-4 w-4" /> Send Reminder</Button>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-ink-900">Calendar</h2>
          <ChevronDown className="h-5 w-5 text-ink-500" />
        </div>
        <div className="mt-5 border-t pt-4">
          <div className="mb-4 flex items-center justify-between text-sm">
            <span>October 2023</span>
            <span className="text-xl text-zinc-300">&lt; &gt;</span>
          </div>
          <div className="grid grid-cols-7 gap-2 text-center text-xs text-ink-500">
            {['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30'].map((day) => (
              <span key={day} className={day === '24' ? 'mx-auto grid h-9 w-9 place-items-center rounded-full border border-coral-500 text-ink-900' : 'py-2'}>{day}</span>
            ))}
          </div>
        </div>
        <div className="mt-4 flex items-center justify-between">
          <h3 className="text-xl font-bold text-ink-900">Upcoming</h3>
          <button className="text-xs text-coral-500 underline">View All</button>
        </div>
        <div className="mt-3 space-y-2">
          {["Monthly doctor's meet", 'Check up', 'Check up'].map((title, index) => (
            <div key={title + index} className="flex items-center gap-3 rounded-lg bg-clinic-green p-3">
              <img className="h-10 w-10 rounded-full object-cover" alt="" src="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=80&q=80" />
              <div>
                <p className="font-bold text-ink-900">{title}</p>
                <p className="text-xs text-ink-500">{index === 0 ? '27' : '29'} October. 2023 | 04:00 PM</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-5">
        <h2 className="text-xl font-bold text-ink-900">Quick Actions</h2>
        <div className="mt-4 divide-y border-t">
          {quickActions.map(([title, subtitle, Icon]) => (
            <button key={title as string} className="flex w-full items-center gap-4 py-5 text-left">
              <span className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-zinc-100 text-ink-500"><Icon className="h-5 w-5" /></span>
              <span className="min-w-0 flex-1">
                <span className="block font-bold text-ink-900">{title}</span>
                <span className="block text-sm text-ink-500">{subtitle}</span>
              </span>
              <ChevronRight className="h-6 w-6 text-ink-500" />
            </button>
          ))}
        </div>
      </Card>
    </div>
  );
}

function RecentConsultations() {
  return (
    <Card className="p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-bold text-ink-900">Recent Consultations</h2>
        <button className="flex items-center gap-2 font-bold text-ink-500">See all <ChevronRight className="h-5 w-5" /></button>
      </div>
      <div className="grid divide-y border md:grid-cols-2 md:divide-x md:divide-y-0">
        {[0, 1].map((column) => (
          <div key={column} className="divide-y">
            {recentConsultations.map(([name, role, image]) => (
              <div key={`${column}-${name}`} className="flex items-center gap-3 p-4">
                <span className="relative">
                  <img className="h-10 w-10 rounded-full object-cover" alt="" src={image} />
                  <span className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white bg-green-600" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block font-semibold text-ink-900">{name}</span>
                  <span className="block text-sm text-ink-500">{role}</span>
                </span>
                <Button variant="secondary" className="min-h-9 px-4">Message</Button>
              </div>
            ))}
          </div>
        ))}
      </div>
    </Card>
  );
}

function DashboardView({ onStartIntake }: { onStartIntake: () => void }) {
  return (
    <PatientPortalShell onStartIntake={onStartIntake}>
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-black">Welcome Jack</h1>
          <p className="text-ink-500">It's a sunny day today, we hope you're taking good care of your health.</p>
        </div>
        <Button onClick={onStartIntake} className="sm:hidden"><Plus className="h-4 w-4" /> New Health Activity</Button>
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,672px)_minmax(340px,414px)]">
        <div className="min-w-0 space-y-4">
          <AppointmentCard />
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <MetricCard icon={<Droplet className="h-7 w-7" />} title="Blood Glucose" value="102" unit="/ 72 mmhg" tone="cyan"><Sparkline /></MetricCard>
            <MetricCard icon={<HeartPulse className="h-7 w-7" />} title="Blood Pressure" value="98" unit="bpm" tone="rose"><Sparkline color="#ef6f77" /></MetricCard>
            <MetricCard icon={<TestTube2 className="h-7 w-7" />} title="Cholesterol Levels" value="139" unit="mg / dL" tone="amber"><Sparkline color="#fb961c" /></MetricCard>
          </div>
          <ActivityGrowthCard />
          <RecentConsultations />
        </div>
        <RightColumn onStartIntake={onStartIntake} />
      </div>
    </PatientPortalShell>
  );
}

export function IntakePage() {
  const [view, setView] = useState<PatientPortalView>('dashboard');
  const [patientRef, setPatientRef] = useState<string | null>(null);

  if (view === 'intake') {
    return (
      <IntakeForm
        onBack={() => setView('dashboard')}
        onSubmitted={(referenceId) => {
          setPatientRef(referenceId);
          setView('confirmation');
        }}
      />
    );
  }

  if (view === 'confirmation') {
    return (
      <ConfirmationScreen
        referenceId={patientRef ?? 'Pending'}
        onBackHome={() => setView('dashboard')}
        onNewIntake={() => {
          setPatientRef(null);
          setView('intake');
        }}
      />
    );
  }

  return <DashboardView onStartIntake={() => setView('intake')} />;
}
