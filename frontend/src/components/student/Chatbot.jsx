import { MessageCircle, Send, X } from 'lucide-react'
import { useMemo, useState } from 'react'

const quickReplies = ['Show resume tips', 'How to improve placement score?', 'Best projects for AI role?']

const getBotResponse = (message) => {
  const lower = message.toLowerCase()
  if (lower.includes('resume')) {
    return 'Start with impact bullets: action + metric + outcome. I can also suggest keyword improvements.'
  }
  if (lower.includes('placement')) {
    return 'Increase projects and internship experience. Focus on communication and mock interviews this week.'
  }
  return 'Great question! I recommend reviewing your Skill Gap and Learning Roadmap for next best actions.'
}

export default function Chatbot() {
  const [open, setOpen] = useState(false)
  const [typing, setTyping] = useState(false)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: 'Hi! I am your career assistant. Ask me anything about your roadmap.',
      at: new Date(),
    },
  ])

  const formatTime = useMemo(
    () =>
      new Intl.DateTimeFormat('en', {
        hour: '2-digit',
        minute: '2-digit',
      }),
    [],
  )

  const pushMessage = (sender, text) => {
    setMessages((prev) => [...prev, { id: prev.length + 1, sender, text, at: new Date() }])
  }

  const handleSend = (value) => {
    const text = value.trim()
    if (!text) {
      return
    }

    pushMessage('user', text)
    setInput('')
    setTyping(true)

    setTimeout(() => {
      pushMessage('bot', getBotResponse(text))
      setTyping(false)
    }, 800)
  }

  return (
    <>
      <button
        className="fixed bottom-6 right-6 z-40 rounded-full bg-indigo-600 p-4 text-white shadow-lg transition hover:scale-105 hover:bg-indigo-500"
        onClick={() => setOpen((prev) => !prev)}
        type="button"
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </button>

      {open ? (
        <div className="fixed bottom-24 right-6 z-40 flex h-[450px] w-[340px] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
          <div className="border-b bg-indigo-600 px-4 py-3 text-sm font-semibold text-white">Career Assistant</div>

          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {messages.map((message) => (
              <div
                className={`max-w-[85%] rounded-xl px-3 py-2 text-sm ${
                  message.sender === 'bot' ? 'bg-slate-100 text-slate-800' : 'ml-auto bg-indigo-600 text-white'
                }`}
                key={message.id}
              >
                <p>{message.text}</p>
                <span className="mt-1 block text-[11px] opacity-70">{formatTime.format(message.at)}</span>
              </div>
            ))}
            {typing ? <p className="text-xs italic text-slate-500">Assistant is typing...</p> : null}
          </div>

          <div className="border-t p-3">
            <div className="mb-2 flex flex-wrap gap-2">
              {quickReplies.map((item) => (
                <button
                  className="rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs text-indigo-700 hover:bg-indigo-100"
                  key={item}
                  onClick={() => handleSend(item)}
                  type="button"
                >
                  {item}
                </button>
              ))}
            </div>
            <form
              className="flex items-center gap-2"
              onSubmit={(event) => {
                event.preventDefault()
                handleSend(input)
              }}
            >
              <input
                className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none ring-indigo-500 focus:ring-2"
                onChange={(event) => setInput(event.target.value)}
                placeholder="Type your message"
                value={input}
              />
              <button className="rounded-lg bg-indigo-600 p-2 text-white hover:bg-indigo-500" type="submit">
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      ) : null}
    </>
  )
}
