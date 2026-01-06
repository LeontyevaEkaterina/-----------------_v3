import React from "react";

const Login: React.FC = () => {
  const handleLogin = async () => {
    try {
      const res = await fetch("/api/v1/auth/google/login", {
        method: "GET",
        credentials: "include"
      });
      if (!res.ok) {
        // TODO: показать пользователю дружелюбную ошибку
        return;
      }
      const data: { authorization_url: string } = await res.json();
      window.location.href = data.authorization_url;
    } catch {
      // TODO: обработать сетевую ошибку
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-slate-50">
      <div className="w-full max-w-md px-6 py-8 bg-slate-800 rounded-xl shadow-lg">
        <h1 className="text-2xl font-semibold mb-4 text-center">
          Чат с нейросетями
        </h1>
        <p className="text-sm text-slate-300 mb-6 text-center">
          Войдите через Google, чтобы начать диалог с моделями.
        </p>
        <button
          type="button"
          onClick={handleLogin}
          className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-white text-slate-900 py-2.5 text-sm font-medium hover:bg-slate-100 transition-colors"
        >
          <span>Войти через Google</span>
        </button>
      </div>
    </div>
  );
};

export default Login;

