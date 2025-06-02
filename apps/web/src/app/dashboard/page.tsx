"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "../../supabaseClient";

const Dashboard = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState<any>(null);

  useEffect(() => {
    const getSession = async () => {
      const { data } = await supabase.auth.getSession();
      setSession(data.session);
      setLoading(false);
      if (!data.session) {
        router.replace("/");
      }
    };
    getSession();
  }, [router]);

  if (loading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.replace("/");
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-white">
      <div className="mb-6 text-2xl font-bold">Welcome to your Dashboard!</div>
      <div className="mb-8 text-gray-700">You are logged in as {session?.user?.email}.</div>
      <a
        href="/settings"
        className="px-6 py-3 bg-blue-600 text-white rounded shadow hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
        tabIndex={0}
        aria-label="Go to settings"
        onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') window.location.href = '/settings'; }}
      >
        Settings
      </a>
      <button
        onClick={handleLogout}
        className="mt-8 px-6 py-3 bg-gray-200 text-gray-900 rounded shadow hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400"
        tabIndex={0}
        aria-label="Log out"
        onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') handleLogout(); }}
      >
        Log out
      </button>
    </main>
  );
};

export default Dashboard;
