// frontend/src/components/RefinementStepper.tsx
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

interface StepperProps {
  stage: 'idle' | 'lexical' | 'semantic' | 'completed';
}

export const RefinementStepper = ({ stage }: StepperProps) => {
  if (stage === 'idle') return null;

  const stages = [
    { id: 'lexical', label: 'Sanitización Mecánica', desc: 'Borrando muletillas y ruidos' },
    { id: 'semantic', label: 'Análisis Semántico', desc: 'Dando coherencia y estructura' },
  ];

  return (
    <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 space-y-4">
      <h4 className="text-xs font-bold uppercase text-slate-500">Estado del Refinamiento</h4>
      <div className="space-y-3">
        {stages.map((s, idx) => (
          <div key={s.id} className="flex items-start gap-3">
            <div className="mt-0.5">
              {stage === s.id ? (
                <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
              ) : (idx === 0 && stage === 'semantic') || stage === 'completed' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              ) : (
                <Circle className="w-4 h-4 text-slate-300" />
              )}
            </div>
            <div>
              <p className={`text-sm font-medium ${stage === s.id ? 'text-blue-600' : 'text-slate-600'}`}>
                {s.label}
              </p>
              <p className="text-[10px] text-slate-400">{s.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
