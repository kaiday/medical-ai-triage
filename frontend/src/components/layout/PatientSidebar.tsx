import {
  Activity,
  BarChart3,
  Calendar,
  FileText,
  Headphones,
  Home,
  Hospital,
  LogOut,
  Settings,
  Stethoscope,
} from 'lucide-react';

const primaryNav = [
  { label: 'Dashboard', icon: Home, active: true },
  { label: 'Consult a Doctor', icon: Stethoscope },
  { label: 'Appointments', icon: Calendar },
  { label: 'Medical History', icon: FileText },
  { label: 'My Hospitals', icon: Hospital },
  { label: 'Analytics', icon: BarChart3 },
];

const secondaryNav = [
  { label: 'Settings', icon: Settings },
  { label: 'Help Center', icon: Headphones },
  { label: 'Refer family & friends', icon: Activity },
];

interface PatientSidebarProps {
  onStartIntake: () => void;
}

export function PatientSidebar({ onStartIntake }: PatientSidebarProps) {
  return (
    <aside className="hidden min-h-screen w-[272px] shrink-0 flex-col bg-brand-700 px-2 py-8 text-white lg:flex">
      <div className="mx-4 mb-5 h-[75px] rounded-full bg-white" aria-label="Medical AI Triage logo placeholder" />

      <nav className="space-y-1" aria-label="Patient portal">
        {primaryNav.map((item) => {
          const Icon = item.icon;
          const isStart = item.label === 'Consult a Doctor';
          return (
            <button
              className={`flex min-h-11 w-full items-center gap-3 rounded-full px-4 text-left text-[15px] font-medium transition ${
                item.active ? 'bg-brand-500 text-white' : 'text-white/70 hover:bg-white/10 hover:text-white'
              }`}
              key={item.label}
              onClick={isStart ? onStartIntake : undefined}
              type="button"
            >
              <Icon size={20} strokeWidth={1.9} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="mt-6 border-t border-white/35 pt-5">
        <p className="mb-4 px-4 text-sm font-semibold text-white">Integrations</p>
        <div className="space-y-1">
          <a className="flex min-h-11 items-center gap-3 rounded-full px-4 text-[15px] font-medium text-white/70 hover:bg-white/10" href="#">
            <span className="grid size-5 place-items-center rounded bg-white text-xs font-bold text-blue-500">G</span>
            Google Drive
          </a>
          <a className="flex min-h-11 items-center gap-3 rounded-full px-4 text-[15px] font-medium text-white/70 hover:bg-white/10" href="#">
            <span className="text-lg font-bold text-blue-500">P</span>
            Paypal
          </a>
        </div>
      </div>

      <div className="mt-auto space-y-1">
        {secondaryNav.map((item) => {
          const Icon = item.icon;
          return (
            <a className="flex min-h-11 items-center gap-3 rounded-full px-4 text-[15px] font-medium text-white/70 hover:bg-white/10" href="#" key={item.label}>
              <Icon size={20} strokeWidth={1.9} />
              {item.label}
            </a>
          );
        })}

        <div className="flex items-center gap-3 px-4 pt-8">
          <div className="relative size-11 rounded-full bg-coral-50 ring-2 ring-white">
            <div className="absolute inset-2 rounded-full bg-coral-500" />
            <span className="absolute -bottom-0.5 -right-0.5 size-3 rounded-full border-2 border-white bg-emerald-500" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-bold">Jack Ezendu</p>
            <p className="truncate text-sm text-white/75">Jack@rayna.ui</p>
          </div>
          <LogOut size={20} />
        </div>
      </div>
    </aside>
  );
}
