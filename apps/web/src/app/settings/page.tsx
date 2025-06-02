"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "../../supabaseClient";

const preferenceOptions = {
  tone: ["friendly", "professional", "humorous"],
  style: ["concise", "detailed"],
  days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
};

const Settings = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState<any>(null);
  type PreferencesForm = {
  preferred_days: string[];
  preferred_times: string;
  buffer_minutes: number;
  tone: string;
  style: string;
};

const [form, setForm] = useState<PreferencesForm>({
  preferred_days: [],
  preferred_times: "",
  buffer_minutes: 15,
  tone: "professional",
  style: "concise",
});

  useEffect(() => {
    const getSessionAndPrefs = async () => {
      const { data } = await supabase.auth.getSession();
      if (!data.session) {
        router.replace("/");
        return;
      }
      setSession(data.session);
      // Fetch preferences from Supabase
      const { data: prefs, error } = await supabase
        .from("preferences")
        .select("preferred_days, preferred_times, buffer_minutes, tone, style")
        .eq("user_id", data.session.user.id)
        .maybeSingle();
      if (!error && prefs) {
        setForm({
          preferred_days: prefs.preferred_days || [],
          preferred_times: prefs.preferred_times || "",
          buffer_minutes: prefs.buffer_minutes ?? 15,
          tone: prefs.tone || "professional",
          style: prefs.style || "concise",
        });
      }
      setLoading(false);
    };
    getSessionAndPrefs();
  }, [router]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked;
      setForm((prev) => ({
        ...prev,
        preferred_days: checked
          ? [...prev.preferred_days, value]
          : prev.preferred_days.filter((d) => d !== value),
      }));
    } else if (type === "number") {
      setForm((prev) => ({ ...prev, [name]: Number(value) }));
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
    }
  };


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!session) return;
    const now = new Date().toISOString();
    const { error } = await supabase.from("preferences")
      .upsert([
        {
          user_id: session.user.id,
          preferred_days: form.preferred_days,
          preferred_times: form.preferred_times,
          buffer_minutes: form.buffer_minutes,
          tone: form.tone,
          style: form.style,
          created_at: now,
          updated_at: now,
        }
      ], { onConflict: 'user_id' });
    if (!error) {
      alert("Preferences saved!");
    } else {
      alert("Failed to save preferences");
    }
  };


  if (loading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-white">
      <form className="flex flex-col gap-6 w-full max-w-md p-8 bg-gray-50 rounded shadow" onSubmit={handleSubmit}>
        <h1 className="text-2xl font-bold text-gray-900 mb-4">User Preferences</h1>
        <div>
          <label className="font-semibold">Preferred Days:</label>
          <div className="flex flex-wrap gap-2 mt-1">
            {preferenceOptions.days.map((day) => (
              <label key={day} className="flex items-center gap-1">
                <input
                  type="checkbox"
                  name="preferred_days"
                  value={day}
                  checked={form.preferred_days.includes(day)}
                  onChange={handleChange}
                  className="accent-blue-600"
                />
                <span>{day}</span>
              </label>
            ))}
          </div>
        </div>
        <div>
          <label className="font-semibold">Preferred Times:</label>
          <input
            type="text"
            name="preferred_times"
            value={form.preferred_times}
            onChange={handleChange}
            placeholder="e.g. 09:00-11:00, 14:00-17:00"
            className="w-full border p-2 rounded mt-1"
          />
        </div>
        <div>
          <label className="font-semibold">Buffer (minutes):</label>
          <input
            type="number"
            name="buffer_minutes"
            value={form.buffer_minutes}
            onChange={handleChange}
            min={0}
            className="w-full border p-2 rounded mt-1"
          />
        </div>
        <div>
          <label className="font-semibold">Tone:</label>
          <select
            name="tone"
            value={form.tone}
            onChange={handleChange}
            className="w-full border p-2 rounded mt-1"
          >
            {preferenceOptions.tone.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="font-semibold">Style:</label>
          <select
            name="style"
            value={form.style}
            onChange={handleChange}
            className="w-full border p-2 rounded mt-1"
          >
            {preferenceOptions.style.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <button type="submit" className="mt-4 px-6 py-3 bg-blue-600 text-white rounded shadow hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400">
          Save Preferences
        </button>
      </form>
    </main>
  );
};

export default Settings;
