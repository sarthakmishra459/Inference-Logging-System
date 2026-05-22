"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { ArrowLeft, Gauge, Server, TriangleAlert, Zap } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { DashboardMetrics } from "@/lib/types";

const numberFormatter = new Intl.NumberFormat("en");

function StatCard({
  title,
  value,
  icon: Icon
}: {
  title: string;
  value: string;
  icon: LucideIcon;
}) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm text-muted-foreground">{title}</CardTitle>
        <Icon size={18} className="text-primary" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-semibold">{value}</div>
      </CardContent>
    </Card>
  );
}

export function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .metrics()
      .then(setMetrics)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load metrics"));
  }, []);

  return (
    <main className="h-screen overflow-y-auto bg-background px-4 py-6 text-foreground">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Analytics</h1>
            <p className="mt-1 text-sm text-muted-foreground">Inference health across the last seven days.</p>
          </div>
          <Button asChild variant="secondary">
            <Link href="/">
              <ArrowLeft size={17} />
              Chat
            </Link>
          </Button>
        </div>

        {error && (
          <div className="mb-4 rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {!metrics ? (
          <div className="flex h-96 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        ) : (
          <>
            <div className="grid gap-4 md:grid-cols-4">
              <StatCard
                title="Average latency"
                value={`${numberFormatter.format(metrics.average_latency_ms)} ms`}
                icon={Gauge}
              />
              <StatCard
                title="Total requests"
                value={numberFormatter.format(metrics.total_requests)}
                icon={Server}
              />
              <StatCard title="Token usage" value={numberFormatter.format(metrics.total_tokens)} icon={Zap} />
              <StatCard title="Error rate" value={`${metrics.error_rate}%`} icon={TriangleAlert} />
            </div>

            <div className="mt-4 grid gap-4 lg:grid-cols-3">
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>Requests over time</CardTitle>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={metrics.requests_over_time}>
                      <defs>
                        <linearGradient id="requests" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.7} />
                          <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0.05} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="timestamp" tick={{ fill: "#94a3b8", fontSize: 12 }} minTickGap={32} />
                      <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} allowDecimals={false} />
                      <Tooltip contentStyle={{ background: "#111827", border: "1px solid #334155" }} />
                      <Area type="monotone" dataKey="requests" stroke="#2dd4bf" fill="url(#requests)" />
                      <Area type="monotone" dataKey="errors" stroke="#f87171" fill="#f8717133" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Provider usage</CardTitle>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={metrics.provider_usage}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                      <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} allowDecimals={false} />
                      <Tooltip contentStyle={{ background: "#111827", border: "1px solid #334155" }} />
                      <Bar dataKey="value" fill="#2dd4bf" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className="lg:col-span-3">
                <CardHeader>
                  <CardTitle>Model usage</CardTitle>
                </CardHeader>
                <CardContent className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={metrics.model_usage}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                      <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} allowDecimals={false} />
                      <Tooltip contentStyle={{ background: "#111827", border: "1px solid #334155" }} />
                      <Bar dataKey="value" fill="#60a5fa" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
