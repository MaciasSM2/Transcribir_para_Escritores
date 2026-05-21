'use client';
import React, { useState, useMemo } from 'react';
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import {
  ChevronDown,
  ChevronUp,
  AlertCircle,
  AlertTriangle,
  Info,
  TrendingUp,
  BookOpen,
  Zap,
} from 'lucide-react';

// ─── Tipos ────────────────────────────────────────────────────────────────────

interface StyleAlert {
  type: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  sentence_index?: number;
}

interface StyleReport {
  sentence_count?: number;
  word_count?: number;
  avg_sentence_len?: number;
  sentence_len_stddev?: number;
  ttr?: number;
  adjective_density?: number;
  flesch_score?: number;
  fernandez_huerta?: number;
  dominant_verb_tense?: string;
  alignment_score?: number;
  profile?: {
    avg_sentence_len?: number;
    ttr_target?: number;
    adjective_density?: number;
    flesch_target?: number;
    reference_author?: string;
    style_display_name?: string;
  };
}

interface Suggestion {
  type: string;
  original: string;
  replacement: string;
  pos: string;
  intensity: string;
  context: string;
}

interface StyleReportPanelProps {
  styleReport: StyleReport;
  alerts: StyleAlert[];
  suggestions: Suggestion[];
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function clamp(val: number, min: number, max: number): number {
  return Math.min(Math.max(val, min), max);
}

/** Normaliza una métrica a escala 0-100 relativa a su target. */
function toRadarValue(user: number, target: number, tolerance = 0.5): number {
  if (!target) return 50;
  const deviation = Math.abs(user - target) / target;
  return Math.round(clamp((1 - deviation / tolerance) * 100, 0, 100));
}

const SEVERITY_CONFIG = {
  critical: {
    icon: <AlertCircle size={15} className="shrink-0 text-red-500" />,
    badge: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
    border: 'border-red-200 dark:border-red-800',
    label: 'Crítico',
  },
  warning: {
    icon: <AlertTriangle size={15} className="shrink-0 text-amber-500" />,
    badge: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
    border: 'border-amber-200 dark:border-amber-800',
    label: 'Advertencia',
  },
  info: {
    icon: <Info size={15} className="shrink-0 text-blue-500" />,
    badge: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
    border: 'border-blue-200 dark:border-blue-800',
    label: 'Info',
  },
};

const ALERT_TYPE_LABELS: Record<string, string> = {
  rhythm:      'Ritmo',
  forbidden:   'Palabra prohibida',
  vicio_mente: 'Vicio -mente',
  queísmo:     'Queísmo',
  structure:   'Estructura POS',
  monotonía:   'Monotonía',
};

// ─── Sub-componente: Score Bar ────────────────────────────────────────────────

function ScoreBar({ score, author }: { score: number; author?: string }) {
  const pct = Math.round(score);
  const colorClass =
    pct >= 70
      ? 'from-emerald-500 to-green-400'
      : pct >= 40
      ? 'from-amber-500 to-yellow-400'
      : 'from-red-500 to-rose-400';

  const label =
    pct >= 70 ? 'Alineación alta' : pct >= 40 ? 'Alineación media' : 'Alineación baja';

  return (
    <div className="mb-5">
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-2">
          <TrendingUp size={15} className="text-purple-500" />
          <span className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wide">
            Alineamiento con el perfil
          </span>
        </div>
        <span className="text-xl font-bold text-slate-800 dark:text-slate-100">{pct}%</span>
      </div>

      {/* Barra de progreso */}
      <div className="relative h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`absolute inset-y-0 left-0 rounded-full bg-gradient-to-r ${colorClass} transition-all duration-700 ease-out`}
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="flex items-center justify-between mt-1">
        <span className="text-[11px] text-slate-400">{label}</span>
        {author && (
          <span className="text-[11px] text-slate-400 flex items-center gap-1">
            <BookOpen size={10} />
            Ref: {author}
          </span>
        )}
      </div>
    </div>
  );
}

// ─── Sub-componente: Radar Chart ──────────────────────────────────────────────

function StyleDNAChart({ report }: { report: StyleReport }) {
  const profile = report.profile ?? {};

  const radarData = useMemo(() => [
    {
      axis: 'Ritmo',
      usuario: toRadarValue(report.avg_sentence_len ?? 0, profile.avg_sentence_len ?? 12, 0.5),
      perfil: 100,
    },
    {
      axis: 'Riqueza Léx.',
      usuario: toRadarValue(report.ttr ?? 0, profile.ttr_target ?? 0.5, 0.4),
      perfil: 100,
    },
    {
      axis: 'Legibilidad',
      usuario: toRadarValue(report.flesch_score ?? 50, profile.flesch_target ?? 55, 0.4),
      perfil: 100,
    },
    {
      axis: 'Adjetivos',
      usuario: toRadarValue(report.adjective_density ?? 0, profile.adjective_density ?? 0.3, 0.5),
      perfil: 100,
    },
    {
      axis: 'Precisión',
      usuario: clamp(Math.round((report.ttr ?? 0.5) * 100), 0, 100),
      perfil: 80,
    },
  ], [report, profile]);

  return (
    <div className="mb-5">
      <div className="flex items-center gap-2 mb-3">
        <Zap size={15} className="text-purple-500" />
        <span className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wide">
          ADN Literario
        </span>
        <div className="flex items-center gap-3 ml-auto text-[10px] text-slate-400">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-purple-500 inline-block" />
            Tu texto
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-600 inline-block" />
            Perfil objetivo
          </span>
        </div>
      </div>
      <div className="h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
            <PolarGrid stroke="#e2e8f0" className="dark:stroke-slate-700" />
            <PolarAngleAxis
              dataKey="axis"
              tick={{ fontSize: 11, fill: '#94a3b8' }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={false}
              axisLine={false}
              tickLine={false}
            />
            <Radar
              name="Perfil"
              dataKey="perfil"
              stroke="#cbd5e1"
              fill="#cbd5e1"
              fillOpacity={0.15}
              strokeDasharray="4 2"
              strokeWidth={1.5}
            />
            <Radar
              name="Tu texto"
              dataKey="usuario"
              stroke="#9333ea"
              fill="#9333ea"
              fillOpacity={0.25}
              strokeWidth={2}
            />
            <Tooltip
              contentStyle={{
                background: '#1e1b4b',
                border: 'none',
                borderRadius: '8px',
                fontSize: '11px',
                color: '#e2e8f0',
              }}
              formatter={(value, name) => [`${value}%`, name as string]}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ─── Sub-componente: Lista de Alertas ─────────────────────────────────────────

function AlertsList({ alerts }: { alerts: StyleAlert[] }) {
  if (!alerts || alerts.length === 0) {
    return (
      <p className="text-xs text-slate-400 text-center py-3">
        ✓ Sin alertas estructurales para este fragmento.
      </p>
    );
  }

  // Ordenar: critical → warning → info
  const sorted = [...alerts].sort((a, b) => {
    const order = { critical: 0, warning: 1, info: 2 };
    return order[a.severity] - order[b.severity];
  });

  return (
    <div className="space-y-2">
      {sorted.map((alert, idx) => {
        const cfg = SEVERITY_CONFIG[alert.severity] ?? SEVERITY_CONFIG.info;
        const typeLabel = ALERT_TYPE_LABELS[alert.type] ?? alert.type;
        return (
          <div
            key={idx}
            className={`flex gap-2.5 p-3 rounded-lg border ${cfg.border} bg-white dark:bg-slate-900/50`}
          >
            <div className="pt-0.5">{cfg.icon}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${cfg.badge}`}>
                  {typeLabel}
                </span>
                {alert.sentence_index !== undefined && (
                  <span className="text-[10px] text-slate-400">frase #{alert.sentence_index + 1}</span>
                )}
              </div>
              <p className="text-[12px] text-slate-600 dark:text-slate-300 leading-relaxed">
                {alert.message}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── Sub-componente: Lista de Sugerencias ─────────────────────────────────────

function SuggestionsList({ suggestions }: { suggestions: Suggestion[] }) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="mb-4">
      <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2">
        Sustituciones aplicadas ({suggestions.length})
      </p>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((s, i) => (
          <div
            key={i}
            className="flex items-center gap-1 text-[11px] bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full px-2.5 py-1"
          >
            <span className="text-red-400 line-through">{s.original}</span>
            <span className="text-slate-400 mx-0.5">→</span>
            <span className="text-emerald-600 dark:text-emerald-400 font-medium">{s.replacement}</span>
            <span className="text-slate-300 dark:text-slate-600 ml-1 text-[9px]">[{s.pos}]</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Componente principal ─────────────────────────────────────────────────────

export default function StyleReportPanel({
  styleReport,
  alerts,
  suggestions,
}: StyleReportPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  const hasContent =
    (styleReport && Object.keys(styleReport).length > 0) ||
    (alerts && alerts.length > 0);

  if (!hasContent) return null;

  const alignmentScore = styleReport?.alignment_score ?? 0;
  const referenceAuthor = styleReport?.profile?.reference_author;
  const criticalCount = alerts?.filter((a) => a.severity === 'critical').length ?? 0;
  const warningCount = alerts?.filter((a) => a.severity === 'warning').length ?? 0;

  return (
    <div className="mt-6 rounded-2xl border border-purple-100 dark:border-purple-900/40 bg-gradient-to-b from-slate-50 to-white dark:from-slate-900/60 dark:to-slate-900/80 shadow-sm overflow-hidden">
      {/* ── Cabecera colapsable ── */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-purple-50/50 dark:hover:bg-purple-900/10 transition-colors"
        aria-expanded={isOpen}
        id="style-report-toggle"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/40 flex items-center justify-center">
            <Zap size={16} className="text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">
              Informe de Estilo Literario
            </h3>
            <p className="text-[11px] text-slate-400">
              Score {Math.round(alignmentScore)}%
              {criticalCount > 0 && (
                <span className="ml-2 text-red-500 font-semibold">
                  · {criticalCount} crítico{criticalCount > 1 ? 's' : ''}
                </span>
              )}
              {warningCount > 0 && (
                <span className="ml-2 text-amber-500 font-semibold">
                  · {warningCount} aviso{warningCount > 1 ? 's' : ''}
                </span>
              )}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <span className="text-[11px]">{isOpen ? 'Cerrar' : 'Ver diagnóstico'}</span>
          {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </button>

      {/* ── Cuerpo del panel ── */}
      {isOpen && (
        <div className="px-5 pb-5 border-t border-purple-100 dark:border-purple-900/30 pt-4 space-y-1 animate-in fade-in slide-in-from-top-2 duration-200">

          {/* Score + Radar en dos columnas en pantallas medianas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            <div>
              <ScoreBar score={alignmentScore} author={referenceAuthor} />
              {/* Métricas rápidas */}
              <div className="grid grid-cols-3 gap-2 mt-4">
                {[
                  { label: 'Palabras', value: styleReport?.word_count ?? '—' },
                  { label: 'Frases', value: styleReport?.sentence_count ?? '—' },
                  { label: 'TTR', value: styleReport?.ttr ? `${Math.round(styleReport.ttr * 100)}%` : '—' },
                  { label: 'Flesch', value: styleReport?.flesch_score ?? '—' },
                  { label: 'Prom. frase', value: styleReport?.avg_sentence_len ? `${styleReport.avg_sentence_len} pal.` : '—' },
                  { label: 'Tiempo verbal', value: styleReport?.dominant_verb_tense ?? '—' },
                ].map((m, i) => (
                  <div
                    key={i}
                    className="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-2.5 text-center"
                  >
                    <p className="text-[11px] text-slate-400 mb-0.5">{m.label}</p>
                    <p className="text-sm font-bold text-slate-700 dark:text-slate-200">
                      {String(m.value)}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <StyleDNAChart report={styleReport} />
          </div>

          {/* Sugerencias léxicas */}
          <SuggestionsList suggestions={suggestions} />

          {/* Alertas estructurales */}
          <div>
            <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2">
              Alertas estructurales ({alerts?.length ?? 0})
            </p>
            <AlertsList alerts={alerts} />
          </div>
        </div>
      )}
    </div>
  );
}
