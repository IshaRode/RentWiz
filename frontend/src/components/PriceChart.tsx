'use client';
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Cell, Legend,
  PieChart, Pie
} from 'recharts';
import type { DealResult } from '@/types';
import { formatRentFull } from '@/lib/api';

const COLORS = {
  good_deal: '#10b981',
  fair: '#f59e0b',
  overpriced: '#ef4444',
};

interface PriceChartProps {
  deals: DealResult[];
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{payload: DealResult}> }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as DealResult;
  return (
    <div className="glass-card p-3 text-xs max-w-[200px]">
      <p className="font-semibold text-white mb-1">{d.title || `${d.bhk}BHK`}</p>
      <p className="text-gray-400">{d.location || d.city}</p>
      <div className="mt-2 space-y-1">
        <p>Area: <span className="text-white">{d.area_sqft.toLocaleString()} sq ft</span></p>
        <p>Actual: <span className="text-white">{formatRentFull(d.actual_rent)}</span></p>
        <p>Predicted: <span className="text-emerald-400">{formatRentFull(d.predicted_rent)}</span></p>
      </div>
    </div>
  );
};

export function ScatterPlot({ deals }: PriceChartProps) {
  const data = deals.map(d => ({
    ...d,
    x: d.area_sqft,
    y: d.actual_rent,
    fill: COLORS[d.deal_label],
  }));

  return (
    <ResponsiveContainer width="100%" height={320}>
      <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis
          dataKey="x" name="Area (sq ft)" type="number"
          tick={{ fill: '#6b7280', fontSize: 11 }}
          label={{ value: 'Area (sq ft)', position: 'bottom', fill: '#6b7280', fontSize: 12 }}
          tickFormatter={v => `${(v/1000).toFixed(1)}k`}
        />
        <YAxis
          dataKey="y" name="Actual Rent" type="number"
          tick={{ fill: '#6b7280', fontSize: 11 }}
          tickFormatter={v => `₹${(v/1000).toFixed(0)}k`}
          width={60}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3', stroke: '#374151' }} />
        <Scatter data={data} fill="#7c3aed">
          {data.map((entry, index) => (
            <Cell key={index} fill={entry.fill} fillOpacity={0.8} />
          ))}
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  );
}

export function RentByBHKChart({ data }: { data: { bhk: number; avg_rent: number; count: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis dataKey="bhk" tick={{ fill: '#6b7280', fontSize: 12 }}
          tickFormatter={v => `${v}BHK`} />
        <YAxis tick={{ fill: '#6b7280', fontSize: 11 }}
          tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} width={60} />
        <Tooltip
          cursor={{ fill: 'transparent' }}
          contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '0.75rem', color: '#fff' }}
          itemStyle={{ color: '#fff' }}
          labelStyle={{ color: '#fff' }}
          formatter={(v: any) => [formatRentFull(Number(v)), 'Avg Rent']}
        />
        <Bar dataKey="avg_rent" radius={[6, 6, 0, 0]} activeBar={false} style={{ outline: 'none' }}>
          {data.map((_, i) => (
            <Cell key={i} fill={`hsl(${250 + i * 30}, 70%, 65%)`} style={{ outline: 'none' }} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function DealDistributionPie({
  distribution
}: { distribution: { good_deal: number; fair: number; overpriced: number } }) {
  const pieData = [
    { name: 'Great Deals', value: distribution.good_deal, color: COLORS.good_deal },
    { name: 'Fair Price', value: distribution.fair, color: COLORS.fair },
    { name: 'Overpriced', value: distribution.overpriced, color: COLORS.overpriced },
  ];

  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={pieData} cx="50%" cy="45%" outerRadius={90} innerRadius={50}
          dataKey="value" paddingAngle={4}
          label={({ name, percent = 0 }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
          labelLine={{ stroke: '#4b5563', strokeWidth: 1 }}
        >
          {pieData.map((entry, i) => (
            <Cell key={i} fill={entry.color} fillOpacity={0.85} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '0.75rem', color: '#fff' }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
