import React from "react";
import type { UserMe } from "../types/api";

interface ChatLayoutProps {
  user: UserMe;
}

const ChatLayout: React.FC<ChatLayoutProps> = ({ user }) => {
  return (
    <div className="min-h-screen flex bg-slate-900 text-slate-50">
      <aside className="hidden md:flex md:w-72 flex-col border-r border-slate-800 bg-slate-950">
        <div className="px-4 py-4 border-b border-slate-800">
          <h1 className="text-lg font-semibold">Чаты</h1>
        </div>
        <div className="flex-1 overflow-y-auto px-2 py-3 text-sm text-slate-400">
          {/* TODO: список диалогов пользователя */}
          <p>Здесь будет список диалогов.</p>
        </div>
      </aside>

      <main className="flex-1 flex flex-col">
        <header className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-center gap-2">
            <div className="md:hidden">
              {/* TODO: кнопка открытия списка диалогов на мобильных */}
            </div>
            <h2 className="text-base font-semibold">Новый диалог</h2>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-slate-300 truncate max-w-[160px]">
              {user.name || user.email}
            </span>
            {user.avatar_url && (
              <img
                src={user.avatar_url}
                alt={user.name ?? user.email}
                className="h-8 w-8 rounded-full border border-slate-700"
              />
            )}
          </div>
        </header>

        <section className="flex-1 flex flex-col items-center justify-center px-4">
          {/* TODO: история сообщений и поле ввода */}
          <p className="text-slate-300 mb-2">
            Добро пожаловать в чат с нейросетями.
          </p>
          <p className="text-slate-500 text-sm">
            Здесь появится история диалогов и окно общения с моделями.
          </p>
        </section>
      </main>
    </div>
  );
};

export default ChatLayout;

