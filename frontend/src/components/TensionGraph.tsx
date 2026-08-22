import React from 'react';
import { AreaChart, Area, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity } from 'lucide-react';

export function TensionGraph({ data }: { data: any[] }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-800 dark:text-slate-200">
        <Activity className="text-red-500" /> Pulso de la Narración
      </h3>
      
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <Tooltip 
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-slate-800 p-3 rounded-lg shadow-xl border border-slate-700 max-w-xs">
                      <p className="text-red-400 font-bold">Tensión: {payload[0].value}/10</p>
                      {payload[0].payload.pacing && (
                        <p className="text-xs text-slate-300 font-medium mb-1">Ritmo: {payload[0].payload.pacing}</p>
                      )}
                      <p className="text-xs text-white leading-relaxed">{payload[0].payload.suggestion}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Area 
              type="monotone" 
              dataKey="score" 
              stroke="#ef4444" 
              fillOpacity={1} 
              fill="url(#colorScore)" 
              strokeWidth={3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-slate-500 mt-4 italic">
        * Las crestas indican clímax o acción. Los valles indican introspección o descripción.
      </p>
    </div>
  );
}
