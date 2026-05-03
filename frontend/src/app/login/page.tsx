"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/store/auth-store";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

type FormValues = z.infer<typeof schema>;

const QUICK_ACCOUNTS = [
  { label: "Admin", email: "admin@acme.test", password: "Admin@12345" },
  { label: "Auditor", email: "auditor@acme.test", password: "Auditor@12345" },
  { label: "Department", email: "dept@acme.test", password: "Dept@12345" },
] as const;

export default function LoginPage() {
  const login = useAuthStore((s) => s.login);
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { email: "", password: "" } });

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      const user = await login(values.email, values.password);
      router.replace(`/dashboard/${user.role}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed");
    }
  }

  function fillDemo(email: string, password: string) {
    setValue("email", email);
    setValue("password", password);
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left: brand panel */}
      <div className="hidden lg:flex bg-gradient-to-br from-brand-800 to-brand-900 text-white p-12 flex-col justify-between">
        <div>
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-8 h-8" />
            <span className="font-semibold tracking-tight">Compliance Audit Manager</span>
          </div>
        </div>
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="space-y-4 max-w-md"
        >
          <h1 className="text-3xl font-bold leading-tight">
            AI-Assisted Smart Compliance Reporting and Audit Management.
          </h1>
          <p className="text-brand-100/90">
            Replace spreadsheets and email chains with a single, auditor-driven platform.
            AI handles the repetitive checks, your team handles the judgment.
          </p>
          <ul className="text-sm text-brand-100/80 space-y-2 pt-2">
            <li>• Audit lifecycle &amp; task workflows</li>
            <li>• Evidence upload + AI OCR pre-screening</li>
            <li>• Findings, corrective actions, dashboards, reports</li>
          </ul>
        </motion.div>
        <p className="text-xs text-brand-100/60">
          v1.0.0 · MVP scaffold
        </p>
      </div>

      {/* Right: form */}
      <div className="flex items-center justify-center p-6">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Sign in</CardTitle>
            <CardDescription>Use your work email and password.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="you@company.com" autoFocus {...register("email")} />
                {errors.email && <p className="text-xs text-red-600">{errors.email.message}</p>}
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" placeholder="••••••••" {...register("password")} />
                {errors.password && <p className="text-xs text-red-600">{errors.password.message}</p>}
              </div>
              {error && (
                <div className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
                  {error}
                </div>
              )}
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Signing in…" : "Sign in"}
              </Button>
            </form>

            <div className="mt-6 pt-6 border-t border-slate-200">
              <p className="text-xs uppercase tracking-wider text-slate-500 mb-2">Demo accounts</p>
              <div className="grid grid-cols-3 gap-2">
                {QUICK_ACCOUNTS.map((a) => (
                  <Button
                    key={a.email}
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => fillDemo(a.email, a.password)}
                  >
                    {a.label}
                  </Button>
                ))}
              </div>
              <p className="text-xs text-slate-400 mt-2">
                Tap a role to fill credentials, then Sign in.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
