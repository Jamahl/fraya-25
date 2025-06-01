"use client";
import { useCallback, useState, useEffect } from "react";
import { supabase } from "../supabaseClient";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

import { useRouter } from "next/navigation";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const router = useRouter();

  // Redirect to dashboard if already logged in
  useEffect(() => {
    const checkSession = async () => {
      const { data } = await supabase.auth.getSession();
      if (data.session) {
        router.replace("/dashboard");
      }
    };
    checkSession();
  }, [router]);

  const handleGoogleLogin = useCallback(async () => {
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      const { error: loginError } = await supabase.auth.signInWithOAuth({ provider: "google" });
      if (loginError) {
        setError("Google sign-in failed. Please try again.");
        setLoading(false);
        return;
      }
      // Wait for redirect and session
      setSuccess("Google sign-in successful. Retrieving session...");
      setTimeout(handleStoreToken, 1500); // Give time for session to update
    } catch (err) {
      setError("Unexpected error during Google sign-in.");
      setLoading(false);
    }
  }, []);

  const handleStoreToken = useCallback(async () => {
    try {
      const { data, error: sessionError } = await supabase.auth.getSession();
      if (sessionError || !data?.session) {
        setError("Could not retrieve Supabase session. Try logging in again.");
        setLoading(false);
        return;
      }
      const provider_token = (data.session as any).provider_token;
      const refresh_token = provider_token?.refresh_token || provider_token?.refreshToken;
      const user_id = data.session.user?.id;
      const email = data.session.user?.email;
      if (!refresh_token || !user_id) {
        setError("Could not extract Google refresh token or user ID. Try logging in again.");
        setLoading(false);
        return;
      }
      const resp = await fetch(`${BACKEND_URL}/api/store-google-token/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id, refresh_token, email }),
      });
      const respJson = await resp.json();
      if (!resp.ok) {
        setError(respJson.error || "Failed to store Google token on backend.");
        setLoading(false);
        return;
      }
      setSuccess("Google refresh token stored successfully!");
      // Redirect to dashboard after success
      window.location.href = "/dashboard";
    } catch (err) {
      setError("Unexpected error during token sync. Try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <main className="flex min-h-screen items-center justify-center bg-white">
      <div className="flex flex-col items-center gap-8">
        <h1 className="text-4xl font-bold text-gray-900">Fraya: Sign in with Google</h1>
        <button
          className="px-6 py-3 bg-blue-600 text-white rounded shadow hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50"
          onClick={handleGoogleLogin}
          tabIndex={0}
          aria-label="Sign in with Google"
          onKeyDown={e => { if (e.key === 'Enter') handleGoogleLogin(); }}
          disabled={loading}
        >
          {loading ? "Signing in..." : "Sign in with Google"}
        </button>
        {error && <div className="text-red-600 mt-2" role="alert">{error}</div>}
        {success && <div className="text-green-600 mt-2" role="status">{success}</div>}
      </div>
    </main>
  );
}
