"use client";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="p-8 text-red-600">
      <h2>Something went wrong!</h2>
      <pre>{error.message}</pre>
      <button onClick={() => reset()} className="mt-4 px-4 py-2 bg-red-100 rounded">Try again</button>
    </div>
  );
}
