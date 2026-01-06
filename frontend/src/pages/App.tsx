import React, { useEffect, useState } from "react";
import Login from "./Login";
import ChatLayout from "./ChatLayout";
import type { UserMe } from "../types/api";

const App: React.FC = () => {
  const [user, setUser] = useState<UserMe | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSession = async () => {
      try {
        const res = await fetch("/api/v1/auth/session", {
          method: "GET",
          credentials: "include"
        });
        if (!res.ok) {
          setUser(null);
          return;
        }
        const data = (await res.json()) as UserMe | null;
        setUser(data);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    void loadSession();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-slate-50">
        <div className="text-sm text-slate-300">Загрузка...</div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return <ChatLayout user={user} />;
};

export default App;



